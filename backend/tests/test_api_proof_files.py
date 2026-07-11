"""Tests des pièces jointes de preuves : stockage local, remplacement, garde-fous."""

import io
import zipfile


def _create_proof(client) -> dict:
    return client.post(
        "/api/proofs", json={"type": "document", "title": "Attestation"}
    ).json()


def _attach(client, proof_id: str, filename: str, content: bytes):
    return client.put(
        f"/api/proofs/{proof_id}/file",
        files={"file": (filename, content, "application/octet-stream")},
    )


def test_attach_and_download_roundtrip(client, tmp_path):
    proof = _create_proof(client)
    response = _attach(client, proof["id"], "attestation.pdf", b"contenu du document")
    assert response.status_code == 200
    file_name = response.json()["file_name"]
    assert file_name.startswith("proofs/")
    assert (tmp_path / file_name).is_file()

    download = client.get(f"/api/proofs/{proof['id']}/file")
    assert download.status_code == 200
    assert download.content == b"contenu du document"
    assert "attestation.pdf" in download.headers["content-disposition"]


def test_attach_replaces_previous_file(client, tmp_path):
    proof = _create_proof(client)
    first = _attach(client, proof["id"], "v1.txt", b"premier").json()["file_name"]
    second = _attach(client, proof["id"], "v2.txt", b"second").json()["file_name"]

    assert not (tmp_path / first).exists(), "l'ancienne pièce doit être remplacée"
    assert (tmp_path / second).is_file()
    assert client.get(f"/api/proofs/{proof['id']}/file").content == b"second"


def test_attach_neutralizes_path_traversal_filename(client, tmp_path):
    proof = _create_proof(client)
    response = _attach(client, proof["id"], "../../evil.txt", b"x")
    assert response.status_code == 200
    file_name = response.json()["file_name"]
    assert ".." not in file_name
    assert (tmp_path / file_name).resolve().is_relative_to(tmp_path.resolve())


def test_download_without_attachment_is_404(client):
    proof = _create_proof(client)
    assert client.get(f"/api/proofs/{proof['id']}/file").status_code == 404


def test_attach_rejects_empty_file(client):
    proof = _create_proof(client)
    assert _attach(client, proof["id"], "vide.txt", b"").status_code == 400


def test_backup_export_includes_attachments(client):
    proof = _create_proof(client)
    _attach(client, proof["id"], "piece.txt", b"preuve")
    export = client.get("/api/backup/export")
    names = zipfile.ZipFile(io.BytesIO(export.content)).namelist()
    assert any(name.startswith("proofs/") for name in names)
