"""Backup ZIP — incarnation de « tes données t'appartiennent » (exigence V1).

Export : archive du dossier de données (base copiée de façon cohérente via
l'API de backup SQLite, + fichiers de preuves). Import : restauration complète,
la base courante est remplacée après validation du contenu.
"""

from __future__ import annotations

import io
import sqlite3
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from app.core.config import DB_FILENAME, resolve_data_dir
from app.core.db import reset_engine, run_migrations

_SQLITE_MAGIC = b"SQLite format 3\x00"


def export_backup() -> tuple[bytes, str]:
    """ZIP du dossier de données. Retourne (contenu, nom de fichier)."""
    data_dir = resolve_data_dir()
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        db_path = data_dir / DB_FILENAME
        if db_path.exists():
            archive.writestr(DB_FILENAME, _consistent_db_copy(db_path))
        # Tout le reste du dossier (fichiers de preuves…), base exclue.
        for path in sorted(data_dir.rglob("*")):
            if path.is_file() and path.name != DB_FILENAME:
                archive.write(path, path.relative_to(data_dir).as_posix())

    stamp = datetime.now(UTC).strftime("%Y-%m-%d")
    return buffer.getvalue(), f"cvforge-backup-{stamp}.zip"


def import_backup(content: bytes) -> None:
    """Restaure un backup : valide l'archive puis remplace les données.

    Lève ``ValueError`` (→ 400) si l'archive n'est pas un backup CVForge.
    """
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as exc:
        raise ValueError("Le fichier fourni n'est pas une archive ZIP.") from exc

    names = archive.namelist()
    if DB_FILENAME not in names:
        raise ValueError(f"Archive invalide : {DB_FILENAME} absent du backup.")

    db_bytes = archive.read(DB_FILENAME)
    if not db_bytes.startswith(_SQLITE_MAGIC):
        raise ValueError("Archive invalide : la base n'est pas un fichier SQLite.")

    data_dir = resolve_data_dir()
    reset_engine()  # libère le fichier avant remplacement (verrou Windows)
    (data_dir / DB_FILENAME).write_bytes(db_bytes)

    for name in names:
        member = Path(name)
        # Garde-fou zip-slip : jamais d'écriture hors du dossier de données.
        if member.is_absolute() or ".." in member.parts or name == DB_FILENAME:
            continue
        target = data_dir / member
        if name.endswith("/"):
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(name))

    # Un backup d'une version plus ancienne est amené au schéma courant.
    run_migrations()


def _consistent_db_copy(db_path: Path) -> bytes:
    """Copie cohérente de la base, même si l'application est en cours d'usage."""
    source = sqlite3.connect(db_path)
    try:
        target = sqlite3.connect(":memory:")
        try:
            source.backup(target)
            return target.serialize()
        finally:
            target.close()
    finally:
        source.close()
