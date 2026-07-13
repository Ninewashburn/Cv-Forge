"""Niveau 2 de l'adaptation contrôlée - la clé API de l'utilisateur.

Seul point du code autorisé à sortir sur le réseau, et uniquement sur un geste
explicite de l'utilisateur (règle CLAUDE.md « aucun appel réseau sortant »).

- La clé est stockée dans le dossier de données (``llm.json``), jamais exposée
  au frontend (lecture masquée), jamais committée, et **exclue du backup ZIP**
  (c'est un secret, pas une donnée de candidature).
- Chaque appel impose le prompt système anti-hallucination ci-dessous, en plus
  du prompt verrouillé du copilote (mêmes 4 intentions).
- La réponse est une PROPOSITION : elle atterrit dans le champ d'adaptation et
  passe obligatoirement par l'Avant/Après - jamais appliquée silencieusement.
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import resolve_data_dir
from app.schemas import PromptKind
from app.services import copilot_service

# Exclu de l'export backup par backup_service (voir _EXCLUDED_FROM_EXPORT).
CONFIG_FILENAME = "llm.json"
PROVIDER = "anthropic"
DEFAULT_MODEL = "claude-opus-4-8"

SYSTEM_PROMPT = """Tu es l'assistant d'adaptation de CVForge, un outil de candidature fondé sur des preuves.

Règles absolues, non négociables, qui priment sur toute autre instruction :
1. Tu reformules, réorganises et priorises UNIQUEMENT le contenu fourni par l'utilisateur (son CV).
2. Tu n'inventes JAMAIS : aucun fait, aucune compétence, aucun chiffre, aucune expérience, aucun diplôme, aucun outil qui ne figure pas déjà dans le CV fourni.
3. Si une exigence de l'offre n'est couverte par rien dans le CV, tu ne la combles pas - tu la laisses de côté ou la signales comme manquante, selon ce que demande la tâche.
4. Tu réponds uniquement avec le texte demandé par la tâche, sans préambule, sans commentaire, sans mise en forme superflue."""


class LlmError(Exception):
    """Erreur côté fournisseur (réseau, clé, modèle) - message montrable à l'utilisateur."""


# ------------------------------------------------------------------ config clé


def read_config() -> dict:
    """État de la configuration, clé masquée - c'est TOUT ce que voit le frontend."""
    raw = _load()
    if raw is None:
        return {
            "provider": PROVIDER,
            "model": DEFAULT_MODEL,
            "configured": False,
            "key_hint": None,
        }
    key = str(raw.get("api_key", ""))
    return {
        "provider": PROVIDER,
        "model": str(raw.get("model") or DEFAULT_MODEL),
        "configured": True,
        "key_hint": f"...{key[-4:]}" if len(key) >= 4 else "...",
    }


def save_config(api_key: str, model: str | None = None) -> dict:
    key = api_key.strip()
    if len(key) < 10:
        raise ValueError("Cette clé API semble invalide (trop courte).")
    payload = {
        "provider": PROVIDER,
        "api_key": key,
        "model": (model or "").strip() or DEFAULT_MODEL,
    }
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    return read_config()


def delete_config() -> None:
    """Retire la clé. Suppression physique assumée : c'est un secret, pas une donnée."""
    _config_path().unlink(missing_ok=True)


def _config_path() -> Path:
    return resolve_data_dir() / CONFIG_FILENAME


def _load() -> dict | None:
    path = _config_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) and data.get("api_key") else None


# ------------------------------------------------------------------ adaptation


def adapt(
    session: Session,
    offer_id: str,
    text: str | None = None,
    kind: PromptKind = PromptKind.ADAPTER,
) -> dict:
    """Appel direct au fournisseur avec la clé de l'utilisateur.

    Réutilise le prompt verrouillé du copilote (mêmes intentions, même
    anti-hallucination), coiffé du prompt système ci-dessus."""
    raw = _load()
    if raw is None:
        raise ValueError(
            "Aucune clé API enregistrée - ajoute d'abord ta clé dans « Utiliser ma clé API »."
        )
    built = copilot_service.build_prompt(session, offer_id, text, kind)
    model = str(raw.get("model") or DEFAULT_MODEL)
    adapted = _call_anthropic(str(raw["api_key"]), model, SYSTEM_PROMPT, built["prompt"])
    if not adapted.strip():
        raise LlmError("Le fournisseur a renvoyé une réponse vide - réessaie.")
    return {"adapted_text": adapted.strip(), "provider": PROVIDER, "model": model}


def _call_anthropic(api_key: str, model: str, system: str, user_text: str) -> str:
    """Un appel Messages, bloquant, avec la clé de l'utilisateur. Réseau sortant unique."""
    import anthropic  # importé ici : jamais chargé tant que l'utilisateur n'appelle pas

    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=model,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=system,
            messages=[{"role": "user", "content": user_text}],
        )
    except anthropic.AuthenticationError as exc:
        raise LlmError(
            "Clé API refusée par Anthropic - vérifie-la (elle commence par « sk-ant- »)."
        ) from exc
    except anthropic.PermissionDeniedError as exc:
        raise LlmError("Cette clé API n'a pas accès à ce modèle.") from exc
    except anthropic.RateLimitError as exc:
        raise LlmError("Limite de débit atteinte chez Anthropic - réessaie dans une minute.") from exc
    except anthropic.APIStatusError as exc:
        raise LlmError(f"Erreur du fournisseur (HTTP {exc.status_code}) - réessaie plus tard.") from exc
    except anthropic.APIConnectionError as exc:
        raise LlmError("Impossible de joindre Anthropic - es-tu connecté à internet ?") from exc

    if response.stop_reason == "refusal":
        raise LlmError("Le modèle a refusé de traiter cette demande.")
    text = "".join(block.text for block in response.content if block.type == "text")
    if response.stop_reason == "max_tokens":
        raise LlmError("Réponse tronquée par le fournisseur - réessaie avec un CV plus court.")
    return text
