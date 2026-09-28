"""Tests for Pydantic validation schemas."""

import pytest
from pydantic import ValidationError

from backend.schemas.case import CaseReferenceCreate
from backend.schemas.source import ContentSourceCreate


def test_valid_case():
    case = CaseReferenceCreate(
        slug="valid-case",
        title="Test Case",
        case_number="1/2024",
        court="Supreme Court",
        case_type="Constitutional",
        decision_date="2024-06-15",
        facts_summary="Some facts.",
        outcome="Allowed.",
        review_status="draft",
    )
    assert case.slug == "valid-case"


def test_invalid_slug_rejected():
    with pytest.raises(ValidationError, match="Invalid slug"):
        CaseReferenceCreate(
            slug="INVALID SLUG!",
            title="T", case_number="1", court="C",
            case_type="T", decision_date="2024-01-01",
            facts_summary="F", outcome="O",
        )


def test_invalid_review_status_rejected():
    with pytest.raises(ValidationError, match="Invalid review_status"):
        CaseReferenceCreate(
            slug="test", title="T", case_number="1", court="C",
            case_type="T", decision_date="2024-01-01",
            facts_summary="F", outcome="O",
            review_status="certified_good_law",
        )


def test_reviewed_status_requires_time():
    with pytest.raises(ValidationError, match="review_time is required"):
        CaseReferenceCreate(
            slug="test", title="T", case_number="1", court="C",
            case_type="T", decision_date="2024-01-01",
            facts_summary="F", outcome="O",
            review_status="metadata_reviewed",
            review_time=None,
        )


def test_content_source_exactly_one_owner():
    with pytest.raises(ValidationError, match="exactly one owner"):
        ContentSourceCreate(
            source_url="https://example.com",
            case_reference_slug="a",
            court_role_slug="b",
        )


def test_content_source_zero_owners():
    with pytest.raises(ValidationError, match="exactly one owner"):
        ContentSourceCreate(source_url="https://example.com")
