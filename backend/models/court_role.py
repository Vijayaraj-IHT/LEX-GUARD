"""CourtRole table."""

from datetime import datetime, timezone

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.enums import ReviewStatus


class CourtRole(Base):
    """Educational description of a court or legal-work role."""

    __tablename__ = "court_roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    review_status: Mapped[str] = mapped_column(
        String(30),
        default=ReviewStatus.DRAFT.value,
        nullable=False,
    )
    review_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    content_sources: Mapped[list["ContentSource"]] = relationship(
        back_populates="court_role"
    )
    workflow_guide_roles: Mapped[list["WorkflowGuideRole"]] = relationship(
        back_populates="court_role"
    )

    def __repr__(self) -> str:
        return f"<CourtRole {self.slug!r}>"
