"""Tests for database constraints and model integrity."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from backend.models.source import Source
from backend.models.case import CaseReference
from backend.models.party import Party, CaseParty
from backend.models.provision import StatutoryProvision


def test_create_source(db_session):
    src = Source(
        title="Test Judgment",
        url="https://example.com/judgment/1",
        publisher="Supreme Court",
        source_type="judgment",
    )
    db_session.add(src)
    db_session.commit()
    assert src.id is not None


def test_source_url_unique(db_session):
    s1 = Source(
        title="Source A", url="https://example.com/dup",
        publisher="Pub", source_type="judgment",
    )
    s2 = Source(
        title="Source B", url="https://example.com/dup",
        publisher="Pub", source_type="legislation",
    )
    db_session.add(s1)
    db_session.commit()
    db_session.add(s2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_case_party_role_on_association(db_session):
    case = CaseReference(
        slug="test-case", title="Test", case_number="1/2024",
        court="HC", case_type="Civil", decision_date=date(2024, 1, 1),
        facts_summary="Facts", outcome="Dismissed",
    )
    party = Party(slug="test-party", name="Petitioner", party_type="individual")
    db_session.add_all([case, party])
    db_session.commit()

    cp = CaseParty(
        case_reference_id=case.id,
        party_id=party.id,
        role_in_case="petitioner",
    )
    db_session.add(cp)
    db_session.commit()
    assert cp.role_in_case == "petitioner"


def test_statutory_provision_unique_act_section(db_session):
    p1 = StatutoryProvision(act_name="Constitution", section_no="368")
    p2 = StatutoryProvision(act_name="Constitution", section_no="368")
    db_session.add(p1)
    db_session.commit()
    db_session.add(p2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
