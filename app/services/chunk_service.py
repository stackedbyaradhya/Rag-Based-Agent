from app.core.config import settings


class ChunkService:
    @staticmethod
    def clean_text(text: str) -> str:
        return " ".join(text.split())

    @staticmethod
    def chunk_text(text: str) -> list[str]:
        cleaned = ChunkService.clean_text(text)
        chunks: list[str] = []
        start = 0
        while start < len(cleaned):
            end = start + settings.chunk_size
            chunks.append(cleaned[start:end])
            if end >= len(cleaned):
                break
            start = end - settings.chunk_overlap
        return chunks
