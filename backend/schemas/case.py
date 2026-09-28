"""CaseReference, CaseIssue, CaseAction schemas (FR-06, 5.5)."""

from datetime import date, datetime
from pydantic import BaseModel, field_validator

from backend.schemas.validators import (
    validate_slug, validate_review_status, validate_positive,
)


class CaseIssueCreate(BaseModel):
    issue_order: int
    description: str

    validate_order = field_validator("issue_order")(validate_positive)


class CaseActionCreate(BaseModel):
    sequence_no: int
    description: str

    validate_seq = field_validator("sequence_no")(validate_positive)


class CaseReferenceCreate(BaseModel):
    """Validated input for a case record (5.5 Required Case Content)."""

    slug: str
    title: str
    case_number: str
    court: str
    case_type: str
    decision_date: date
    citation: str | None = None
    facts_summary: str
    holding_summary: str | None = None
    outcome: str
    procedural_stage: str | None = None
    review_status: str = "draft"
    review_time: datetime | None = None

    validate_slug_field = field_validator("slug")(validate_slug)
    validate_status = field_validator("review_status")(validate_review_status)

    @field_validator("review_time")
    @classmethod
    def reviewed_needs_time(cls, v, info):
        status = info.data.get("review_status", "draft")
        reviewed_statuses = {
            "metadata_reviewed", "file_verified",
        }
        if status in reviewed_statuses and v is None:
            raise ValueError(
                f"review_time is required when review_status is '{status}'"
            )
        return v
