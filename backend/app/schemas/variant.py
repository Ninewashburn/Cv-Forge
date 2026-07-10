"""Schémas I/O des variantes de CV et de leurs phrases tracées."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ReadBase, SentenceStatus, VariantStatus


class GeneratedSentenceRead(ReadBase):
    variant_id: str
    text: str
    source_fact_ids: list[str] = Field(default_factory=list)
    source_proof_ids: list[str] = Field(default_factory=list)
    status: SentenceStatus
    reason: str | None = None
    position: int = 0


class CvVariantCreate(BaseModel):
    profile_id: str
    offer_id: str


class VariantCreateRequest(BaseModel):
    """Corps optionnel de POST /offers/{id}/variants : avec ``adapted_text``,
    la variante porte l'adaptation du wizard (manuelle/copilote) au lieu
    d'être générée depuis les faits."""

    adapted_text: str | None = None


class CvVariantUpdate(BaseModel):
    recommended_title: str | None = None
    recommended_summary: str | None = None
    adapted_text: str | None = None
    status: VariantStatus | None = None


class CvVariantRead(ReadBase):
    profile_id: str
    offer_id: str
    recommended_title: str
    recommended_summary: str
    adapted_text: str
    match_score: int | None = None
    status: VariantStatus
    sentences: list[GeneratedSentenceRead] = Field(default_factory=list)
