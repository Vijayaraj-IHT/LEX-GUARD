"""WorkflowGuide, WorkflowGuideRole, and WorkflowStep tables."""

from datetime import datetime, timezone

from sqlalchemy import (
    String, Text, Integer, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.enums import ReviewStatus


class WorkflowGuide(Base):
    """Structured guide for a publicly documented legal workflow."""

    __tablename__ = "workflow_guides"

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
        back_populates="workflow_guide"
    )
    steps: Mapped[list["WorkflowStep"]] = relationship(
        back_populates="workflow_guide",
        cascade="all, delete-orphan",
        order_by="WorkflowStep.step_number",
    )
    workflow_guide_roles: Mapped[list["WorkflowGuideRole"]] = relationship(
        back_populates="workflow_guide", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<WorkflowGuide {self.slug!r}>"


class WorkflowGuideRole(Base):
    """Many-to-many association between WorkflowGuide and CourtRole."""

    __tablename__ = "workflow_guide_roles"
    __table_args__ = (
        UniqueConstraint(
            "workflow_guide_id", "court_role_id",
            name="uq_workflow_guide_role",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_guide_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_guides.id", ondelete="CASCADE"), nullable=False
    )
    court_role_id: Mapped[int] = mapped_column(
        ForeignKey("court_roles.id", ondelete="CASCADE"), nullable=False
    )

    workflow_guide: Mapped["WorkflowGuide"] = relationship(
        back_populates="workflow_guide_roles"
    )
    court_role: Mapped["CourtRole"] = relationship(
        back_populates="workflow_guide_roles"
    )


class WorkflowStep(Base):
    """Ordered instruction belonging to a workflow guide."""

    __tablename__ = "workflow_steps"
    __table_args__ = (
        UniqueConstraint(
            "workflow_guide_id", "step_number",
            name="uq_workflow_step_number",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    workflow_guide_id: Mapped[int] = mapped_column(
        ForeignKey("workflow_guides.id", ondelete="CASCADE"), nullable=False
    )
    step_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    workflow_guide: Mapped["WorkflowGuide"] = relationship(
        back_populates="steps"
    )

    def __repr__(self) -> str:
        return f"<WorkflowStep {self.step_number}: {self.title!r}>"
