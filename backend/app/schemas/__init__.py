"""Schémas I/O Pydantic v2 — contrat de l'API CVForge."""

from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate
from app.schemas.common import (
    ApplicationStatus,
    Confidentiality,
    FactType,
    ProofType,
    ReadBase,
    SentenceStatus,
    VariantStatus,
)
from app.schemas.fact import FactCreate, FactRead, FactUpdate
from app.schemas.matching import (
    CopilotPromptRead,
    MatchingKeyword,
    MatchingResult,
    MatchRequest,
)
from app.schemas.offer import OfferCreate, OfferRead, OfferUpdate
from app.schemas.profile import (
    MasterProfileCreate,
    MasterProfileRead,
    MasterProfileUpdate,
)
from app.schemas.proof import ProofCreate, ProofRead, ProofUpdate
from app.schemas.variant import (
    CvVariantCreate,
    CvVariantRead,
    CvVariantUpdate,
    GeneratedSentenceRead,
)

__all__ = [
    "ApplicationCreate",
    "ApplicationRead",
    "ApplicationStatus",
    "ApplicationUpdate",
    "Confidentiality",
    "CopilotPromptRead",
    "CvVariantCreate",
    "CvVariantRead",
    "CvVariantUpdate",
    "FactCreate",
    "FactRead",
    "FactType",
    "FactUpdate",
    "GeneratedSentenceRead",
    "MasterProfileCreate",
    "MasterProfileRead",
    "MasterProfileUpdate",
    "MatchRequest",
    "MatchingKeyword",
    "MatchingResult",
    "OfferCreate",
    "OfferRead",
    "OfferUpdate",
    "ProofCreate",
    "ProofRead",
    "ProofType",
    "ProofUpdate",
    "ReadBase",
    "SentenceStatus",
    "VariantStatus",
]
