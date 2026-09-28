"""Shared Pydantic validators."""

import re
from pydantic import field_validator

SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

VALID_REVIEW_STATUSES = {
    "draft", "source_linked", "metadata_reviewed",
    "file_verified", "needs_correction", "superseded", "withdrawn",
}


def validate_slug(v: str) -> str:
    if not SLUG_RE.match(v):
        raise ValueError(
            f"Invalid slug '{v}': must be lowercase alphanumeric with hyphens"
        )
    return v


def validate_review_status(v: str) -> str:
    if v not in VALID_REVIEW_STATUSES:
        raise ValueError(
            f"Invalid review_status '{v}': must be one of {VALID_REVIEW_STATUSES}"
        )
    return v


def validate_sha256(v: str | None) -> str | None:
    if v is not None and not SHA256_RE.match(v):
        raise ValueError(
            f"Invalid SHA-256 '{v}': must be 64 lowercase hex characters"
        )
    return v


def validate_positive(v: int) -> int:
    if v < 1:
        raise ValueError(f"Value must be positive, got {v}")
    return v
