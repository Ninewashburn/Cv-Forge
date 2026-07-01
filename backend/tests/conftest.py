"""Fixtures partagées : client API sur un dossier de données jetable."""

import pytest
from fastapi.testclient import TestClient

from app.core import db as core_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Client HTTP sur une app neuve : CVFORGE_DATA → tmp, migrations réelles
    exécutées par le lifespan au démarrage."""
    monkeypatch.setenv("CVFORGE_DATA", str(tmp_path))
    core_db.reset_engine()
    from app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
    core_db.reset_engine()
