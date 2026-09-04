"""Filets d'erreur globaux : jamais de message technique ou anglais à l'écran.

Le frontend affiche ``detail`` tel quel quand c'est une chaîne. Ces tests
garantissent que c'en est toujours une, en français, pour les 422 et les 500.
"""

from fastapi.testclient import TestClient

from app.core import db as core_db
from app.main import INVALID_REQUEST_MESSAGE, UNEXPECTED_ERROR_MESSAGE, create_app


def test_validation_error_is_a_french_string(client):
    # Corps invalide : ``type`` n'est pas un FactType.
    response = client.post("/api/facts", json={"type": "licorne", "title": "x"})
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, str)
    assert detail == INVALID_REQUEST_MESSAGE


def test_unexpected_error_is_a_french_string(tmp_path, monkeypatch):
    from app.services import backup_service

    def boom() -> None:
        raise RuntimeError("explosion interne")

    # Le router appelle backup_service.export_backup() par attribut de module :
    # on simule un bug imprévu au coeur d'un endpoint réel.
    monkeypatch.setattr(backup_service, "export_backup", boom)
    monkeypatch.setenv("CVFORGE_DATA", str(tmp_path))
    core_db.reset_engine()

    # raise_server_exceptions=False : on veut la réponse HTTP, pas l'exception.
    with TestClient(create_app(), raise_server_exceptions=False) as test_client:
        response = test_client.get("/api/backup/export")
    core_db.reset_engine()

    assert response.status_code == 500
    detail = response.json()["detail"]
    assert detail == UNEXPECTED_ERROR_MESSAGE
    assert "Internal Server Error" not in detail
    assert "explosion interne" not in detail  # la trace ne fuit jamais à l'écran


def test_oversized_upload_is_refused_before_reading(client, monkeypatch):
    from app.services import extract_service

    monkeypatch.setattr(extract_service, "MAX_SIZE_BYTES", 10)
    response = client.post(
        "/api/extract", files={"file": ("gros.txt", b"x" * 11, "text/plain")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == extract_service.TOO_LARGE_MESSAGE
