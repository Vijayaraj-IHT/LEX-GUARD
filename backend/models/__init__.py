"""
LexGuard ORM models — single import point.

Importing this package registers all 13 tables with Base.metadata.
No module/package conflict: this file re-exports every model class.
"""

from backend.models.source import Source, ContentSource
from backend.models.court_role import CourtRole
from backend.models.workflow import WorkflowGuide, WorkflowGuideRole, WorkflowStep
from backend.models.case import CaseReference, CaseIssue, CaseAction
from backend.models.party import Party, CaseParty
from backend.models.provision import StatutoryProvision, CaseProvision

__all__ = [
    "Source",
    "ContentSource",
    "CourtRole",
    "WorkflowGuide",
    "WorkflowGuideRole",
    "WorkflowStep",
    "CaseReference",
    "CaseIssue",
    "CaseAction",
    "Party",
    "CaseParty",
    "StatutoryProvision",
    "CaseProvision",
]
