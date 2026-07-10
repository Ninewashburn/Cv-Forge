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
    CopilotPromptRequest,
    MatchingKeyword,
    MatchingResult,
    MatchRequest,
    PromptKind,
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
    VariantCreateRequest,
)

__all__ = [
    "ApplicationCreate",
    "ApplicationRead",
    "ApplicationStatus",
    "ApplicationUpdate",
    "Confidentiality",
    "CopilotPromptRead",
    "CopilotPromptRequest",
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
    "PromptKind",
    "ProofCreate",
    "ProofRead",
    "ProofType",
    "ProofUpdate",
    "ReadBase",
    "SentenceStatus",
    "VariantCreateRequest",
    "VariantStatus",
]
