"""Party and CaseParty schemas."""

from pydantic import BaseModel, field_validator

from backend.schemas.validators import validate_slug


class PartyCreate(BaseModel):
    slug: str
    name: str
    party_type: str

    validate_slug_field = field_validator("slug")(validate_slug)


class CasePartyCreate(BaseModel):
    party_slug: str
    role_in_case: str
