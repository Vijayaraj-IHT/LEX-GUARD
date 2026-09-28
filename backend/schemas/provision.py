"""StatutoryProvision and CaseProvision schemas."""

from pydantic import BaseModel


class StatutoryProvisionCreate(BaseModel):
    act_name: str
    section_no: str


class CaseProvisionCreate(BaseModel):
    act_name: str
    section_no: str
