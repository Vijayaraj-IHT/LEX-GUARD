"""Shared enumerations used across models and schemas."""

import enum


class ReviewStatus(str, enum.Enum):
    """Content review lifecycle stages (Appendix A of SRS)."""
    DRAFT = "draft"
    SOURCE_LINKED = "source_linked"
    METADATA_REVIEWED = "metadata_reviewed"
    FILE_VERIFIED = "file_verified"
    NEEDS_CORRECTION = "needs_correction"
    SUPERSEDED = "superseded"
    WITHDRAWN = "withdrawn"


class SourceType(str, enum.Enum):
    """Classification of the originating legal source."""
    JUDGMENT = "judgment"
    LEGISLATION = "legislation"
    COURT_RULE = "court_rule"
    OFFICIAL_MANUAL = "official_manual"
    CIRCULAR = "circular"
    INSTITUTIONAL_PUBLICATION = "institutional_publication"


class ContentType(str, enum.Enum):
    """Supported polymorphic content owners for ContentSource."""
    CASE_REFERENCE = "case_reference"
    COURT_ROLE = "court_role"
    WORKFLOW_GUIDE = "workflow_guide"
