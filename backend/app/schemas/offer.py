"""Schémas I/O des offres d'emploi."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ReadBase


class OfferCreate(BaseModel):
    """Import V1 : texte collé uniquement. ``source_url`` est une référence
    saisie par l'utilisateur - jamais fetchée (aucun appel réseau sortant)."""

    raw_text: str = Field(min_length=1)
    title: str = ""
    company: str = ""
    source_url: str | None = None


class OfferUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    source_url: str | None = None
    # Modifier le texte relance l'analyse (mots-clés recalculés).
    raw_text: str | None = Field(default=None, min_length=1)


class OfferRead(ReadBase):
    title: str
    company: str
    raw_text: str
    source_url: str | None = None
    keywords: list = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    optional_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
