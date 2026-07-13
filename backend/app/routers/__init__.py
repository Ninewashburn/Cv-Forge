"""Routers HTTP - fins : validation I/O et délégation aux services."""

from app.routers.applications import router as applications_router
from app.routers.backup import router as backup_router
from app.routers.extract import router as extract_router
from app.routers.facts import router as facts_router
from app.routers.llm import router as llm_router
from app.routers.offers import router as offers_router
from app.routers.profile import router as profile_router
from app.routers.proofs import router as proofs_router
from app.routers.variants import router as variants_router

__all__ = [
    "applications_router",
    "backup_router",
    "extract_router",
    "facts_router",
    "llm_router",
    "offers_router",
    "profile_router",
    "proofs_router",
    "variants_router",
]
