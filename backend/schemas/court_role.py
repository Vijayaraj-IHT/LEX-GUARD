"""CourtRole schema."""

from datetime import datetime
from pydantic import BaseModel, field_validator

from backend.schemas.validators import validate_slug, validate_review_status


class CourtRoleCreate(BaseModel):
    slug: str
    title: str
    description: str | None = None
    review_status: str = "draft"
    review_time: datetime | None = None

    validate_slug_field = field_validator("slug")(validate_slug)
    validate_status = field_validator("review_status")(validate_review_status)
