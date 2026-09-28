"""
Idempotent database seeding with audit reporting (FR-39 through FR-48).

Reads validated JSON from data/reviewed/, skips data/drafts/.
Reports created, updated, skipped, quarantined, and rejected records.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from pydantic import ValidationError

from backend.database import SessionLocal, init_db
from backend.models.source import Source, ContentSource
from backend.models.case import CaseReference, CaseIssue, CaseAction
from backend.models.party import Party, CaseParty
from backend.models.provision import StatutoryProvision, CaseProvision
from backend.schemas.case import CaseReferenceCreate


@dataclass
class SeedReport:
    """Audit report for a seeding run (FR-45, FR-46)."""
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    quarantined: list[str] = field(default_factory=list)
    rejected: list[str] = field(default_factory=list)

    def summary(self) -> str:
        lines = [
            "=== LexGuard Seed Report ===",
            f"  Created:     {len(self.created)}",
            f"  Updated:     {len(self.updated)}",
            f"  Skipped:     {len(self.skipped)}",
            f"  Quarantined: {len(self.quarantined)}",
            f"  Rejected:    {len(self.rejected)}",
        ]
        if self.rejected:
            lines.append("\n  Rejected details:")
            for r in self.rejected:
                lines.append(f"    - {r}")
        if self.quarantined:
            lines.append("\n  Quarantined details:")
            for q in self.quarantined:
                lines.append(f"    - {q}")
        return "\n".join(lines)


def _upsert_case(db: Session, data: dict, report: SeedReport) -> None:
    """Validate and upsert a single case record (FR-39, FR-41, FR-42)."""
    slug = data.get("slug", "<unknown>")

    # FR-24: Pydantic validation before insertion
    try:
        case_data = CaseReferenceCreate(**data)
    except ValidationError as e:
        report.rejected.append(f"{slug}: {e}")
        return

    # FR-33: draft must not be silently promoted
    if case_data.review_status == "draft":
        report.quarantined.append(f"{slug}: draft status — not seeded as reviewed")
        return

    existing = db.query(CaseReference).filter_by(slug=case_data.slug).first()

    if existing:
        # Update mutable fields
        for attr in [
            "title", "case_number", "court", "case_type",
            "decision_date", "citation", "facts_summary",
            "holding_summary", "outcome", "procedural_stage",
            "review_status", "review_time",
        ]:
            setattr(existing, attr, getattr(case_data, attr))
        existing.updated_at = datetime.now(timezone.utc)
        report.updated.append(slug)
    else:
        case = CaseReference(
            **case_data.model_dump(exclude={"review_time"}, exclude_none=False)
        )
        case.review_time = case_data.review_time
        db.add(case)
        report.created.append(slug)


def seed_database(data_dir: str = "data") -> SeedReport:
    """
    Seed the database from reviewed JSON files (FR-43).

    Only reads from data/reviewed/. Drafts are excluded (FR-38).
    Uses a single transaction (FR-40).
    """
    report = SeedReport()
    base = Path(data_dir)
    reviewed_dir = base / "reviewed" / "cases"

    if not reviewed_dir.exists():
        report.skipped.append("No reviewed/cases/ directory found")
        return report

    # Check for drafts and quarantine-report them (FR-36, FR-37)
    drafts_dir = base / "drafts" / "cases"
    if drafts_dir.exists():
        for f in drafts_dir.glob("*.json"):
            report.quarantined.append(
                f"drafts/cases/{f.name}: preserved in draft quarantine"
            )

    init_db()
    db = SessionLocal()

    try:
        for json_file in sorted(reviewed_dir.glob("*.json")):
            try:
                raw = json.loads(json_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError as e:
                report.rejected.append(f"{json_file.name}: invalid JSON — {e}")
                continue

            # Support both single records and lists
            records = raw if isinstance(raw, list) else [raw]
            for record in records:
                _upsert_case(db, record, report)

        db.commit()  # FR-40: transactional
    except Exception as e:
        db.rollback()
        report.rejected.append(f"Transaction failed: {e}")
    finally:
        db.close()

    return report


if __name__ == "__main__":
    report = seed_database()
    print(report.summary())
