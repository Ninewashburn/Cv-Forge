"""Résolution du dossier de données CVForge.

Point d'accès UNIQUE au chemin des données (règle CLAUDE.md : jamais de
chemin en dur ailleurs dans le code). Ordre de résolution :

1. Variable d'environnement ``CVFORGE_DATA`` ;
2. Marqueur ``cvforge.portable`` à côté de l'application → données dans
   ``./data/`` (mode clé USB, activé en V1.5 avec l'exe PyInstaller) ;
3. Défaut : ``~/.cvforge/``.

La logique portable de V1.5 s'ajoutera ici, sans toucher au reste du code.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PORTABLE_MARKER = "cvforge.portable"
DB_FILENAME = "cvforge.db"


def app_dir() -> Path:
    """Dossier de l'application : celui de l'exe une fois gelé (PyInstaller),
    sinon la racine ``backend/`` en développement."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def resolve_data_dir() -> Path:
    """Résout (et crée si besoin) le dossier de données de l'utilisateur."""
    env = os.environ.get("CVFORGE_DATA")
    if env:
        data_dir = Path(env).expanduser()
    elif (app_dir() / PORTABLE_MARKER).exists():
        data_dir = app_dir() / "data"
    else:
        data_dir = Path.home() / ".cvforge"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def database_url() -> str:
    """URL SQLAlchemy de la base SQLite, dérivée de resolve_data_dir()."""
    return f"sqlite:///{resolve_data_dir() / DB_FILENAME}"


def static_dir() -> Path | None:
    """Build Angular servi par FastAPI (single process, Phase 5).

    Point de résolution UNIQUE, comme resolve_data_dir() : dans l'exe
    PyInstaller (V1.5) le build sera embarqué dans ``static/`` à côté du
    binaire ; en dev/local il vit dans ``frontend/dist``. Retourne ``None``
    si aucun build n'existe (mode API seule)."""
    if getattr(sys, "frozen", False):
        candidate = app_dir() / "static"
    else:
        candidate = app_dir().parent / "frontend" / "dist" / "cvforge" / "browser"
    return candidate if (candidate / "index.html").is_file() else None
