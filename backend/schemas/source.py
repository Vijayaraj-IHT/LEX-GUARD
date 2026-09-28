"""Source and ContentSource validation schemas (FR-10 through FR-15)."""

from datetime import datetime
from pydantic import BaseModel, HttpUrl, field_validator, model_validator

from backend.schemas.validators import validate_sha256


class SourceCreate(BaseModel):
    title: str
    url: str
    publisher: str
    source_type: str

    @field_validator("url")
    @classmethod
    def url_must_be_valid(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError(f"URL must start with http:// or https://: {v}")
        return v

    @field_validator("source_type")
    @classmethod
    def source_type_must_be_valid(cls, v: str) -> str:
        valid = {
            "judgment", "legislation", "court_rule",
            "official_manual", "circular", "institutional_publication",
        }
        if v not in valid:
            raise ValueError(f"source_type must be one of {valid}")
        return v


class ContentSourceCreate(BaseModel):
    source_url: str  # Resolved to source_id during seeding
    retrieval_time: datetime | None = None
    source_filename: str | None = None
    source_sha256: str | None = None

    # Exactly one owner identifier
    case_reference_slug: str | None = None
    court_role_slug: str | None = None
    workflow_guide_slug: str | None = None

    validate_hash = field_validator("source_sha256")(validate_sha256)

    @model_validator(mode="after")
    def exactly_one_owner(self) -> "ContentSourceCreate":
        owners = [
            self.case_reference_slug,
            self.court_role_slug,
            self.workflow_guide_slug,
        ]
        non_null = [o for o in owners if o is not None]
        if len(non_null) != 1:
            raise ValueError(
                f"ContentSource must have exactly one owner, got {len(non_null)}"
            )
        return self
