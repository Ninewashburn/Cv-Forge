"""Schémas du niveau clé API (adaptation contrôlée, niveau 2)."""

from pydantic import BaseModel

from app.schemas.matching import PromptKind


class LlmConfigRead(BaseModel):
    """État de la configuration — la clé n'est JAMAIS renvoyée, seulement un indice."""

    provider: str
    model: str
    configured: bool
    key_hint: str | None


class LlmConfigWrite(BaseModel):
    """Saisie de la clé par l'utilisateur (stockée côté backend uniquement)."""

    api_key: str
    model: str | None = None


class AdaptRequest(BaseModel):
    """CV à adapter (absent → profil maître) + intention, comme le copilote."""

    text: str | None = None
    kind: PromptKind = PromptKind.ADAPTER


class AdaptResult(BaseModel):
    """Proposition du fournisseur — à valider dans l'Avant/Après, jamais auto-appliquée."""

    adapted_text: str
    provider: str
    model: str
