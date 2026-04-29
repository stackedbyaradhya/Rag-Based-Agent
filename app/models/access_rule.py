from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin


class AccessRule(Base, TimestampMixin):
    __tablename__ = "access_rules"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(30), nullable=False, default="org_public")
    value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (UniqueConstraint("document_id", "rule_type", "value", name="uq_access_rule"),)
