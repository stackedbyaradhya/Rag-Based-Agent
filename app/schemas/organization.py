from datetime import datetime

from pydantic import BaseModel, Field


class CreateOrganizationRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    slug: str = Field(min_length=2, max_length=255)


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    created_at: datetime
