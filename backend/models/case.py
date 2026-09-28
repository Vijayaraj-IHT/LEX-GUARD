"""CaseReference, CaseIssue, and CaseAction tables."""

from datetime import date, datetime, timezone

from sqlalchemy import (
    String, Text, Date, Integer, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.enums import ReviewStatus


class CaseReference(Base):
    """Structured educational record representing a legal case (FR-06, 5.5)."""

    __tablename__ = "case_references"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    case_number: Mapped[str] = mapped_column(String(200), nullable=False)
    court: Mapped[str] = mapped_column(String(500), nullable=False)
    case_type: Mapped[str] = mapped_column(String(100), nullable=False)
    decision_date: Mapped[date] = mapped_column(Date, nullable=False)
    citation: Mapped[str | None] = mapped_column(String(500), nullable=True)
    facts_summary: Mapped[str] = mapped_column(Text, nullable=False)
    holding_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    outcome: Mapped[str] = mapped_column(Text, nullable=False)
    procedural_stage: Mapped[str | None] = mapped_column(String(200), nullable=True)
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
        back_populates="case_reference"
    )
    case_parties: Mapped[list["CaseParty"]] = relationship(
        back_populates="case_reference", cascade="all, delete-orphan"
    )
    case_provisions: Mapped[list["CaseProvision"]] = relationship(
        back_populates="case_reference", cascade="all, delete-orphan"
    )
    issues: Mapped[list["CaseIssue"]] = relationship(
        back_populates="case_reference",
        cascade="all, delete-orphan",
        order_by="CaseIssue.issue_order",
    )
    actions: Mapped[list["CaseAction"]] = relationship(
        back_populates="case_reference",
        cascade="all, delete-orphan",
        order_by="CaseAction.sequence_no",
    )

    def __repr__(self) -> str:
        return f"<CaseReference {self.slug!r}>"


class CaseIssue(Base):
    """Legal issue recorded for a case."""

    __tablename__ = "case_issues"
    __table_args__ = (
        UniqueConstraint(
            "case_reference_id", "issue_order",
            name="uq_case_issue_order",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_reference_id: Mapped[int] = mapped_column(
        ForeignKey("case_references.id", ondelete="CASCADE"), nullable=False
    )
    issue_order: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    case_reference: Mapped["CaseReference"] = relationship(
        back_populates="issues"
    )


class CaseAction(Base):
    """Ordered procedural action recorded for a case."""

    __tablename__ = "case_actions"
    __table_args__ = (
        UniqueConstraint(
            "case_reference_id", "sequence_no",
            name="uq_case_action_sequence",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_reference_id: Mapped[int] = mapped_column(
        ForeignKey("case_references.id", ondelete="CASCADE"), nullable=False
    )
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    case_reference: Mapped["CaseReference"] = relationship(
        back_populates="actions"
    )
