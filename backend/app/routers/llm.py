"""Configuration du niveau clé API - la clé vit côté backend, jamais côté navigateur."""

from fastapi import APIRouter, HTTPException

from app.schemas import LlmConfigRead, LlmConfigWrite
from app.services import llm_service

router = APIRouter(prefix="/api/llm", tags=["llm"])


@router.get("/config", response_model=LlmConfigRead)
def get_config() -> LlmConfigRead:
    """État de la configuration (clé masquée - seuls 4 caractères d'indice)."""
    return LlmConfigRead.model_validate(llm_service.read_config())


@router.put("/config", response_model=LlmConfigRead)
def save_config(data: LlmConfigWrite) -> LlmConfigRead:
    """Enregistre la clé dans le dossier de données (exclue du backup ZIP)."""
    try:
        return LlmConfigRead.model_validate(llm_service.save_config(data.api_key, data.model))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/config", status_code=204)
def delete_config() -> None:
    """Retire la clé (suppression physique : c'est un secret, pas une donnée)."""
    llm_service.delete_config()
