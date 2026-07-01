"""Schémas I/O des faits (parcours validé)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import FactType, ReadBase


class FactBase(BaseModel):
    type: FactType
    title: str = Field(min_length=1, max_length=300)
    content: str = ""
    tags: list[str] = Field(default_factory=list)
    validated: bool = False
    position: int = 0


class FactCreate(FactBase):
    # Absent → rattaché au profil maître (V1 : un seul profil).
    profile_id: str | None = None


class FactUpdate(BaseModel):
    type: FactType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=300)
    content: str | None = None
    tags: list[str] | None = None
    validated: bool | None = None
    position: int | None = None


class FactRead(FactBase, ReadBase):
    profile_id: str
    proof_ids: list[str] = Field(default_factory=list)
