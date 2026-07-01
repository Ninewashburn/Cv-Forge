"""Briques communes des schémas I/O (Pydantic v2)."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict


class FactType(StrEnum):
    EXPERIENCE = "experience"
    SKILL = "skill"
    PROJECT = "project"
    EDUCATION = "education"
    ACHIEVEMENT = "achievement"


class ProofType(StrEnum):
    NOTE = "note"
    LINK = "link"
    DOCUMENT = "document"


class Confidentiality(StrEnum):
    PRIVATE = "private"
    ANONYMIZED = "anonymized"
    PUBLIC = "public"


class SentenceStatus(StrEnum):
    VALID = "valid"
    REJECTED = "rejected"


class VariantStatus(StrEnum):
    DRAFT = "draft"
    VALIDATED = "validated"


class ApplicationStatus(StrEnum):
    """Micro-tracking V1 — mêmes statuts que CVForge Lite."""

    ENVOYEE = "envoyee"
    REPONSE = "reponse"
    ENTRETIEN = "entretien"
    REFUS = "refus"


class ReadBase(BaseModel):
    """Champs sync-ready exposés en lecture sur toutes les entités."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
