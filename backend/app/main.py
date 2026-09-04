"""CVForge - application FastAPI locale.

Point d'entrée V1 : ``uvicorn app.main:app``. Au démarrage, la base est
créée/migrée automatiquement (l'utilisateur ne lance jamais de migration).
Single process : l'app sert aussi le build Angular quand il existe
(fallback SPA), sur la même origine que l'API.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import static_dir
from app.core.db import run_migrations
from app.routers import (
    applications_router,
    backup_router,
    extract_router,
    facts_router,
    llm_router,
    offers_router,
    profile_router,
    proofs_router,
    variants_router,
)
from app.services.errors import NotFoundError

logger = logging.getLogger("cvforge")

# Messages de repli, en français simple : c'est ce que voit l'utilisateur quand
# rien de plus précis n'a été prévu. La trace technique, elle, va dans le
# journal du serveur - jamais à l'écran.
INVALID_REQUEST_MESSAGE = (
    "Les informations envoyées sont incomplètes ou mal formées. "
    "Vérifie ce que tu as saisi, puis réessaie."
)
UNEXPECTED_ERROR_MESSAGE = (
    "CVForge a rencontré un problème inattendu. Réessaie ; si ça continue, "
    "ferme puis relance l'application. Ton travail enregistré est conservé."
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    run_migrations()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="CVForge API",
        version="0.1.0",
        description="API locale de CVForge - local-first, aucune donnée ne sort.",
        lifespan=lifespan,
    )

    # Dev uniquement : ng serve (4200) appelle l'API (8000) en direct.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(_request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(RequestValidationError)
    async def validation_handler(
        _request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Sans ce filet, FastAPI renvoie une LISTE d'erreurs en anglais : le
        # frontend l'afficherait telle quelle (« [object Object] »).
        logger.warning("Requête invalide : %s", exc.errors())
        return JSONResponse(status_code=422, content={"detail": INVALID_REQUEST_MESSAGE})

    @app.exception_handler(Exception)
    async def unexpected_handler(_request: Request, exc: Exception) -> JSONResponse:
        # Dernier filet : jamais de « Internal Server Error » anglais à l'écran.
        logger.exception("Erreur inattendue : %s", exc)
        return JSONResponse(status_code=500, content={"detail": UNEXPECTED_ERROR_MESSAGE})

    @app.get("/api/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(profile_router)
    app.include_router(facts_router)
    app.include_router(proofs_router)
    app.include_router(offers_router)
    app.include_router(variants_router)
    app.include_router(applications_router)
    app.include_router(backup_router)
    app.include_router(extract_router)
    app.include_router(llm_router)

    # Phase 5 - single process : FastAPI sert le build Angular sur la même
    # origine. Les routes /api ci-dessus restent prioritaires ; toute autre URL
    # sert le fichier demandé s'il existe, sinon index.html (fallback SPA pour
    # les liens profonds comme /atelier). Sans build : mode API seule.
    static = static_dir()
    if static is not None:

        @app.get("/{full_path:path}", include_in_schema=False)
        def spa(full_path: str) -> FileResponse:
            candidate = (static / full_path).resolve()
            if candidate.is_file() and candidate.is_relative_to(static.resolve()):
                return FileResponse(candidate)
            return FileResponse(static / "index.html")

    return app


app = create_app()
