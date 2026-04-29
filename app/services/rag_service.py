from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.models.chat_history import ChatHistory
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.schemas.chat import AskQuestionResponse, ChunkSource
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService


class RAGService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()

    async def ask(self, db: Session, user: User, question: str) -> AskQuestionResponse:
        query_embedding = await self.embedding_service.embed(question)

        stmt = (
            select(DocumentChunk)
            .join(Document, Document.id == DocumentChunk.document_id)
            .options(joinedload(DocumentChunk.document))
            .where(Document.organization_id == user.organization_id)
            .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
            .limit(settings.top_k)
        )
        rows = db.execute(stmt).scalars().all()

        if not rows:
            return AskQuestionResponse(answer="I could not find relevant context to answer this question.", confidence=0.0, sources=[])

        sources: list[ChunkSource] = []
        context_sections: list[str] = []
        for chunk in rows:
            score = float(
                db.scalar(select(1 - DocumentChunk.embedding.cosine_distance(query_embedding)).where(DocumentChunk.id == chunk.id))
                or 0.0
            )
            if score < settings.similarity_threshold:
                continue
            sources.append(
                ChunkSource(
                    document_id=chunk.document_id,
                    document_title=chunk.document.title,
                    chunk_id=chunk.id,
                    chunk_index=chunk.chunk_index,
                    excerpt=chunk.content[:300],
                    score=score,
                )
            )
            context_sections.append(f"[{chunk.document.title}::chunk-{chunk.chunk_index}] {chunk.content}")

        if not sources:
            return AskQuestionResponse(
                answer="I don't have enough reliable context in your knowledgebase to answer that safely.",
                confidence=0.0,
                sources=[],
            )

        answer = await self.llm_service.answer(question=question, context="\n\n".join(context_sections))
        confidence = round(sum(source.score for source in sources) / len(sources), 2)

        db.add(
            ChatHistory(
                user_id=user.id,
                organization_id=user.organization_id,
                question=question,
                answer=answer,
                topic=question[:120],
            )
        )
        db.commit()
        return AskQuestionResponse(answer=answer, confidence=confidence, sources=sources)

    @staticmethod
    def most_searched_topics_today(db: Session, organization_id: int) -> list[str]:
        rows = (
            db.query(ChatHistory.topic, func.count(ChatHistory.id).label("count"))
            .filter(ChatHistory.organization_id == organization_id, ChatHistory.topic.isnot(None))
            .group_by(ChatHistory.topic)
            .order_by(func.count(ChatHistory.id).desc())
            .limit(5)
            .all()
        )
        return [topic for topic, _ in rows if topic]
