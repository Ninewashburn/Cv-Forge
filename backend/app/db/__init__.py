"""Modèles persistants (SQLAlchemy 2.x) de CVForge."""

from app.db.base import Base, SyncReadyMixin
from app.db.models import (
    Application,
    CvVariant,
    Fact,
    GeneratedSentence,
    MasterProfile,
    Offer,
    Proof,
    ProofFact,
)

__all__ = [
    "Application",
    "Base",
    "CvVariant",
    "Fact",
    "GeneratedSentence",
    "MasterProfile",
    "Offer",
    "Proof",
    "ProofFact",
    "SyncReadyMixin",
]
