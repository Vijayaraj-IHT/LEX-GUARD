"""StatutoryProvision and CaseProvision tables."""

from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class StatutoryProvision(Base):
    """Act and section referenced by a case."""

    __tablename__ = "statutory_provisions"
    __table_args__ = (
        UniqueConstraint("act_name", "section_no", name="uq_act_section"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    act_name: Mapped[str] = mapped_column(String(500), nullable=False)
    section_no: Mapped[str] = mapped_column(String(50), nullable=False)

    case_provisions: Mapped[list["CaseProvision"]] = relationship(
        back_populates="provision", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<StatutoryProvision {self.act_name} s.{self.section_no}>"


class CaseProvision(Base):
    """Many-to-many association between CaseReference and StatutoryProvision."""

    __tablename__ = "case_provisions"
    __table_args__ = (
        UniqueConstraint(
            "case_reference_id", "provision_id",
            name="uq_case_provision",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_reference_id: Mapped[int] = mapped_column(
        ForeignKey("case_references.id", ondelete="CASCADE"), nullable=False
    )
    provision_id: Mapped[int] = mapped_column(
        ForeignKey("statutory_provisions.id", ondelete="CASCADE"), nullable=False
    )

    case_reference: Mapped["CaseReference"] = relationship(
        back_populates="case_provisions"
    )
    provision: Mapped["StatutoryProvision"] = relationship(
        back_populates="case_provisions"
    )
