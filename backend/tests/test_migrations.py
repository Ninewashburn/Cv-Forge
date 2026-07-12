"""La première migration Alembic doit créer le schéma complet, seule."""

from pathlib import Path

import pytest
from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command

BACKEND_DIR = Path(__file__).resolve().parents[1]

EXPECTED_TABLES = {
    "master_profile",
    "fact",
    "proof",
    "proof_fact",
    "offer",
    "cv_variant",
    "generated_sentence",
    "application",
}


@pytest.fixture
def migrated_db(tmp_path, monkeypatch):
    monkeypatch.setenv("CVFORGE_DATA", str(tmp_path))
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(cfg, "head")
    return tmp_path / "cvforge.db"


def test_upgrade_head_creates_all_tables(migrated_db):
    engine = create_engine(f"sqlite:///{migrated_db}")
    tables = set(inspect(engine).get_table_names())
    engine.dispose()
    assert EXPECTED_TABLES <= tables


def test_sync_ready_columns_on_every_table(migrated_db):
    engine = create_engine(f"sqlite:///{migrated_db}")
    inspector = inspect(engine)
    for table in EXPECTED_TABLES:
        columns = {c["name"] for c in inspector.get_columns(table)}
        missing = {"id", "created_at", "updated_at", "deleted_at"} - columns
        assert not missing, f"{table} : colonnes sync-ready manquantes {missing}"
    engine.dispose()
