from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import SessionLocal, get_db
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentVisibilityUpdate
from app.services.chunk_service import ChunkService
from app.services.embedding_service import EmbeddingService
from app.services.upload_service import UploadService

router = APIRouter()


async def process_document_chunks(document_id: int, file_path: str) -> None:
    db = SessionLocal()
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return
        document.status = "processing"
        db.commit()

        text = UploadService.extract_text(file_path)
        chunks = ChunkService.chunk_text(text)
        embedding_service = EmbeddingService()
        for idx, chunk in enumerate(chunks):
            embedding = await embedding_service.embed(chunk)
            db.add(DocumentChunk(document_id=document_id, chunk_index=idx, content=chunk, embedding=embedding))
        document.status = "indexed"
        db.commit()
    finally:
        db.close()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved_path, size = await UploadService.save_upload(file)
    document = Document(
        title=file.filename or "Untitled",
        file_name=file.filename or "file",
        file_path=saved_path,
        file_type=(file.filename or "").split(".")[-1].lower(),
        file_size=size,
        status="pending",
        visibility="org_public",
        organization_id=current_user.organization_id,
        uploaded_by_id=current_user.id,
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    background_tasks.add_task(process_document_chunks, document.id, saved_path)
    return DocumentResponse.model_validate(document)


@router.get("", response_model=list[DocumentResponse])
def list_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = db.query(Document).filter(Document.organization_id == current_user.organization_id).all()
    return [DocumentResponse.model_validate(doc) for doc in docs]


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.organization_id == current_user.organization_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id, Document.organization_id == current_user.organization_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    db.delete(doc)
    db.commit()


@router.patch("/{document_id}/visibility", response_model=DocumentResponse)
def update_visibility(
    document_id: int,
    payload: DocumentVisibilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == document_id, Document.organization_id == current_user.organization_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if doc.uploaded_by_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")
    doc.visibility = payload.visibility
    doc.department = payload.department
    db.commit()
    db.refresh(doc)
    return DocumentResponse.model_validate(doc)
