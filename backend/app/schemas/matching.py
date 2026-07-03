"""Schémas I/O du matching et du mode copilote."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    """Texte à matcher contre l'offre. Absent → contenu du profil maître."""

    text: str | None = None


class PromptKind(StrEnum):
    """Intentions de la bibliothèque de prompts verrouillés
    (cf. docs/specs/copilot_prompts.md)."""

    ADAPTER = "adapter"
    AUDITER = "auditer"
    MUSCLER = "muscler"
    ACCROCHER = "accrocher"


class CopilotPromptRequest(BaseModel):
    """Texte de CV (absent → profil maître) + intention choisie."""

    text: str | None = None
    kind: PromptKind = PromptKind.ADAPTER


class MatchingKeyword(BaseModel):
    keyword: str
    frequency: int
    covered: bool


class MatchingResult(BaseModel):
    score: int = Field(ge=0, le=100)
    keywords: list[MatchingKeyword]
    missing: list[str]


class CopilotPromptRead(BaseModel):
    """Prompt verrouillé (anti-hallucination) prêt à coller dans le chat de l'utilisateur."""

    prompt: str
    missing_keywords: list[str]
