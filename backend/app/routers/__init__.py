"""Routers HTTP — fins : validation I/O et délégation aux services."""

from app.routers.facts import router as facts_router
from app.routers.offers import router as offers_router
from app.routers.profile import router as profile_router
from app.routers.proofs import router as proofs_router
from app.routers.variants import router as variants_router

__all__ = [
    "facts_router",
    "offers_router",
    "profile_router",
    "proofs_router",
    "variants_router",
]
