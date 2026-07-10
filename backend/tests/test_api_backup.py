"""Tests du backup ZIP : export cohérent, restauration complète, garde-fous."""

import io
import zipfile


def _zip_names(response) -> list[str]:
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    return zipfile.ZipFile(io.BytesIO(response.content)).namelist()


def test_export_contains_database(client):
    client.get("/api/profile")  # provoque la création de la base
    response = client.get("/api/backup/export")
    assert "cvforge.db" in _zip_names(response)
    assert "cvforge-backup-" in response.headers["content-disposition"]


def test_backup_roundtrip_restores_data(client):
    fact = client.post("/api/facts", json={"type": "skill", "title": "Angular"}).json()
    backup = client.get("/api/backup/export").content

    # On abîme l'état courant : le fait est supprimé, un intrus est ajouté.
    client.delete(f"/api/facts/{fact['id']}")
    client.post("/api/facts", json={"type": "skill", "title": "Intrus"})

    response = client.post(
        "/api/backup/import",
        files={"file": ("backup.zip", backup, "application/zip")},
    )
    assert response.status_code == 204

    titles = [f["title"] for f in client.get("/api/facts").json()]
    assert titles == ["Angular"]  # l'état exporté est revenu, l'intrus a disparu


def test_import_rejects_non_zip(client):
    response = client.post(
        "/api/backup/import",
        files={"file": ("backup.zip", b"pas un zip du tout", "application/zip")},
    )
    assert response.status_code == 400


def test_import_rejects_zip_without_database(client):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("notes.txt", "rien d'utile")
    response = client.post(
        "/api/backup/import",
        files={"file": ("backup.zip", buffer.getvalue(), "application/zip")},
    )
    assert response.status_code == 400
    assert "cvforge.db" in response.json()["detail"]


def test_import_rejects_fake_database(client):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("cvforge.db", b"ceci n'est pas du SQLite")
    response = client.post(
        "/api/backup/import",
        files={"file": ("backup.zip", buffer.getvalue(), "application/zip")},
    )
    assert response.status_code == 400
