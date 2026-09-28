"""Source and ContentSource tables (FR-10 through FR-15)."""

from datetime import datetime, timezone

from sqlalchemy import (
    String, Text, DateTime, ForeignKey, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.enums import SourceType


class Source(Base):
    """An identified official legal source (FR-10, FR-11)."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), unique=True, nullable=False)
    publisher: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # SourceType enum value stored as string
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    content_sources: Mapped[list["ContentSource"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Source {self.title!r}>"


class ContentSource(Base):
    """
    Links exactly one source to exactly one content owner (FR-12–FR-15).

    Exactly one of case_reference_id, court_role_id, workflow_guide_id
    must be non-null — enforced by CHECK constraint.
    """

    __tablename__ = "content_sources"
    __table_args__ = (
        CheckConstraint(
            "(CASE WHEN case_reference_id IS NOT NULL THEN 1 ELSE 0 END) + "
            "(CASE WHEN court_role_id IS NOT NULL THEN 1 ELSE 0 END) + "
            "(CASE WHEN workflow_guide_id IS NOT NULL THEN 1 ELSE 0 END) = 1",
            name="ck_content_source_exactly_one_owner",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        ForeignKey("sources.id", ondelete="CASCADE"), nullable=False
    )
    retrieval_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    source_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_sha256: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )  # FR-21: nullable when no stable file

    # Polymorphic owner FKs — exactly one must be set
    case_reference_id: Mapped[int | None] = mapped_column(
        ForeignKey("case_references.id", ondelete="CASCADE"), nullable=True
    )
    court_role_id: Mapped[int | None] = mapped_column(
        ForeignKey("court_roles.id", ondelete="CASCADE"), nullable=True
    )
    workflow_guide_id: Mapped[int | None] = mapped_column(
        ForeignKey("workflow_guides.id", ondelete="CASCADE"), nullable=True
    )

    # Relationships
    source: Mapped["Source"] = relationship(back_populates="content_sources")
    case_reference: Mapped["CaseReference | None"] = relationship(
        back_populates="content_sources"
    )
    court_role: Mapped["CourtRole | None"] = relationship(
        back_populates="content_sources"
    )
    workflow_guide: Mapped["WorkflowGuide | None"] = relationship(
        back_populates="content_sources"
    )

    def __repr__(self) -> str:
        return f"<ContentSource source_id={self.source_id}>"
