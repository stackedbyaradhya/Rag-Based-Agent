from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    file_name: str
    file_type: str
    file_size: int
    status: str
    visibility: str
    department: str | None
    created_at: datetime


class DocumentVisibilityUpdate(BaseModel):
    visibility: str
    department: str | None = None
