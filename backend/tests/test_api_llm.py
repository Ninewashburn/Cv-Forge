"""Tests du niveau clé API : stockage masqué, adaptation (fournisseur mocké), garde-fous."""

import io
import zipfile

from app.services import llm_service


def _save_key(client, key: str = "sk-ant-test-0000abcd"):
    return client.put("/api/llm/config", json={"api_key": key})


def _create_offer(client) -> dict:
    return client.post(
        "/api/offers",
        json={"raw_text": "Recherche developpeur Angular TypeScript. Angular indispensable."},
    ).json()


def test_config_roundtrip_never_exposes_key(client):
    # Sans clé : non configuré.
    empty = client.get("/api/llm/config").json()
    assert empty == {
        "provider": "anthropic",
        "model": llm_service.DEFAULT_MODEL,
        "configured": False,
        "key_hint": None,
    }

    saved = _save_key(client).json()
    assert saved["configured"] is True
    assert saved["key_hint"] == "...abcd"
    # La clé complète n'apparaît nulle part dans la réponse.
    assert "sk-ant-test-0000abcd" not in str(saved)

    assert client.delete("/api/llm/config").status_code == 204
    assert client.get("/api/llm/config").json()["configured"] is False


def test_config_rejects_short_key(client):
    response = client.put("/api/llm/config", json={"api_key": "abc"})
    assert response.status_code == 400


def test_adapt_without_key_is_400(client):
    offer = _create_offer(client)
    response = client.post(f"/api/offers/{offer['id']}/adapt", json={"text": "Mon CV Angular"})
    assert response.status_code == 400
    assert "clé API" in response.json()["detail"]


def test_adapt_calls_provider_with_system_prompt(client, monkeypatch):
    captured = {}

    def fake_call(api_key, model, system, user_text):
        captured.update(api_key=api_key, model=model, system=system, user_text=user_text)
        return "CV adapté par le modèle.\n"

    monkeypatch.setattr(llm_service, "_call_anthropic", fake_call)
    _save_key(client)
    offer = _create_offer(client)

    response = client.post(
        f"/api/offers/{offer['id']}/adapt",
        json={"text": "Mon CV : Angular, TypeScript.", "kind": "adapter"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "adapted_text": "CV adapté par le modèle.",
        "provider": "anthropic",
        "model": llm_service.DEFAULT_MODEL,
    }
    assert captured["api_key"] == "sk-ant-test-0000abcd"
    # Le prompt système anti-hallucination est imposé, et le prompt copilote
    # (avec le CV de l'utilisateur) part en message utilisateur.
    assert "n'inventes JAMAIS" in captured["system"]
    assert "Angular, TypeScript" in captured["user_text"]


def test_adapt_provider_error_is_502(client, monkeypatch):
    def fake_call(api_key, model, system, user_text):
        raise llm_service.LlmError("Clé API refusée par Anthropic - vérifie-la.")

    monkeypatch.setattr(llm_service, "_call_anthropic", fake_call)
    _save_key(client)
    offer = _create_offer(client)

    response = client.post(f"/api/offers/{offer['id']}/adapt", json={"text": "Mon CV"})
    assert response.status_code == 502
    assert "refusée" in response.json()["detail"]


def test_backup_never_contains_api_key(client):
    _save_key(client)
    export = client.get("/api/backup/export")
    names = zipfile.ZipFile(io.BytesIO(export.content)).namelist()
    assert llm_service.CONFIG_FILENAME not in names


def test_restore_never_overwrites_api_key(client, tmp_path):
    _save_key(client, "sk-ant-locale-conservee")

    # Archive piégée : une base valide + un llm.json étranger.
    db_bytes = client.get("/api/backup/export").content
    inner_db = zipfile.ZipFile(io.BytesIO(db_bytes)).read("cvforge.db")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("cvforge.db", inner_db)
        archive.writestr(llm_service.CONFIG_FILENAME, '{"api_key": "sk-ant-intruse"}')

    response = client.post(
        "/api/backup/import",
        files={"file": ("backup.zip", buffer.getvalue(), "application/zip")},
    )
    assert response.status_code == 204
    assert (tmp_path / llm_service.CONFIG_FILENAME).read_text(encoding="utf-8").find(
        "sk-ant-locale-conservee"
    ) != -1
