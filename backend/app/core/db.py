"""Moteur et sessions SQLAlchemy.

Le moteur est créé paresseusement à partir de :func:`app.core.config.database_url`,
donc toujours via ``resolve_data_dir()``. ``reset_engine()`` permet aux tests de
repartir sur un autre dossier de données (variable ``CVFORGE_DATA``).
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import database_url

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    @event.listens_for(engine, "connect")
    def _set_pragma(dbapi_connection, _record) -> None:  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_engine(
            database_url(), connect_args={"check_same_thread": False}
        )
        _enable_sqlite_foreign_keys(_engine)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            bind=get_engine(), expire_on_commit=False, autoflush=False
        )
    return _session_factory


def get_session() -> Iterator[Session]:
    """Dépendance FastAPI : une session par requête, fermée en fin de requête."""
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def run_migrations() -> None:
    """Amène la base au dernier schéma (``alembic upgrade head``).

    Appelée au démarrage de l'app : l'utilisateur n'a jamais de migration à
    lancer lui-même. Chemins résolus via ``app_dir()`` — fonctionne en dev
    comme dans l'exe PyInstaller (V1.5).
    """
    from alembic.config import Config

    from alembic import command
    from app.core.config import app_dir

    cfg = Config(str(app_dir() / "alembic.ini"))
    cfg.set_main_option("script_location", str(app_dir() / "alembic"))
    command.upgrade(cfg, "head")


def reset_engine() -> None:
    """Ferme le moteur courant (tests / changement de dossier de données)."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
