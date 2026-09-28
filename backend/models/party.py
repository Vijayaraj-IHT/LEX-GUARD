"""Party and CaseParty tables."""

from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


class Party(Base):
    """Person, organisation, government body, or other entity in a case."""

    __tablename__ = "parties"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    party_type: Mapped[str] = mapped_column(String(100), nullable=False)

    case_parties: Mapped[list["CaseParty"]] = relationship(
        back_populates="party", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Party {self.name!r}>"


class CaseParty(Base):
    """Many-to-many association between CaseReference and Party (FR-09)."""

    __tablename__ = "case_parties"
    __table_args__ = (
        UniqueConstraint(
            "case_reference_id", "party_id", "role_in_case",
            name="uq_case_party_role",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_reference_id: Mapped[int] = mapped_column(
        ForeignKey("case_references.id", ondelete="CASCADE"), nullable=False
    )
    party_id: Mapped[int] = mapped_column(
        ForeignKey("parties.id", ondelete="CASCADE"), nullable=False
    )
    role_in_case: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # FR-09: stored on association

    case_reference: Mapped["CaseReference"] = relationship(
        back_populates="case_parties"
    )
    party: Mapped["Party"] = relationship(back_populates="case_parties")
