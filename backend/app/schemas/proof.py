"""Schémas I/O des preuves (banque de preuves)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import Confidentiality, ProofType, ReadBase


class ProofBase(BaseModel):
    type: ProofType
    title: str = Field(min_length=1, max_length=300)
    content: str = ""
    confidentiality: Confidentiality = Confidentiality.PRIVATE


class ProofCreate(ProofBase):
    fact_ids: list[str] = Field(default_factory=list)


class ProofUpdate(BaseModel):
    type: ProofType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=300)
    content: str | None = None
    confidentiality: Confidentiality | None = None
    fact_ids: list[str] | None = None


class ProofRead(ProofBase, ReadBase):
    file_name: str | None = None
    fact_ids: list[str] = Field(default_factory=list)
