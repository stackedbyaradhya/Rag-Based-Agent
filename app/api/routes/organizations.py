from fastapi import APIRouter, Depends, HTTPException, status
from slugify import slugify
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.organization import Organization
from app.schemas.organization import CreateOrganizationRequest, OrganizationResponse

router = APIRouter()


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(payload: CreateOrganizationRequest, db: Session = Depends(get_db)):
    slug = slugify(payload.slug)
    existing = db.query(Organization).filter(Organization.slug == slug).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Slug already exists")
    org = Organization(name=payload.name, slug=slug)
    db.add(org)
    db.commit()
    db.refresh(org)
    return OrganizationResponse(id=org.id, name=org.name, slug=org.slug, created_at=org.created_at)


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(organization_id: int, db: Session = Depends(get_db)):
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return OrganizationResponse(id=org.id, name=org.name, slug=org.slug, created_at=org.created_at)
