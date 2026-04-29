from pathlib import Path
from uuid import uuid4

import docx
import pdfplumber
from fastapi import HTTPException, UploadFile, status
from PyPDF2 import PdfReader

from app.core.config import settings


class UploadService:
    @staticmethod
    def validate(file: UploadFile) -> None:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in settings.allowed_file_extensions:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")

    @staticmethod
    async def save_upload(file: UploadFile) -> tuple[str, int]:
        UploadService.validate(file)
        content = await file.read()
        max_size = settings.max_file_size_mb * 1024 * 1024
        if len(content) > max_size:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File size exceeds limit")

        Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
        ext = Path(file.filename or "").suffix.lower()
        path = str(Path(settings.upload_dir) / f"{uuid4().hex}{ext}")
        Path(path).write_bytes(content)
        return path, len(content)

    @staticmethod
    def extract_text(file_path: str) -> str:
        ext = Path(file_path).suffix.lower()
        if ext == ".txt" or ext == ".md":
            return Path(file_path).read_text(encoding="utf-8", errors="ignore")
        if ext == ".docx":
            d = docx.Document(file_path)
            return "\n".join(p.text for p in d.paragraphs)
        if ext == ".pdf":
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
            if text.strip():
                return text
            reader = PdfReader(file_path)
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported parser")
