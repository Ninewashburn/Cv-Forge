"""Tests de l'API V1 : profil, faits, preuves, offres — CRUD et soft delete."""


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


# ---------------------------------------------------------------- profil

def test_profile_is_created_on_first_access(client):
    body = client.get("/api/profile").json()
    assert body["id"]
    assert body["full_name"] == ""


def test_profile_update(client):
    first = client.get("/api/profile").json()
    updated = client.put(
        "/api/profile", json={"full_name": "Ada Lovelace", "headline": "Développeuse"}
    ).json()
    assert updated["id"] == first["id"]  # toujours le même profil unique
    assert updated["full_name"] == "Ada Lovelace"
    assert client.get("/api/profile").json()["full_name"] == "Ada Lovelace"


# ---------------------------------------------------------------- faits

def _create_fact(client, title="Angular", **extra):
    payload = {"type": "skill", "title": title, **extra}
    response = client.post("/api/facts", json=payload)
    assert response.status_code == 201
    return response.json()


def test_fact_create_resolves_master_profile(client):
    fact = _create_fact(client)
    assert fact["profile_id"] == client.get("/api/profile").json()["id"]


def test_fact_crud_and_soft_delete(client):
    fact = _create_fact(client, tags=["angular", "front"])
    fact_id = fact["id"]

    patched = client.patch(f"/api/facts/{fact_id}", json={"validated": True}).json()
    assert patched["validated"] is True

    assert client.delete(f"/api/facts/{fact_id}").status_code == 204
    assert client.get(f"/api/facts/{fact_id}").status_code == 404
    assert all(f["id"] != fact_id for f in client.get("/api/facts").json())


def test_fact_invalid_type_rejected(client):
    response = client.post("/api/facts", json={"type": "magie", "title": "X"})
    assert response.status_code == 422


# ---------------------------------------------------------------- preuves

def test_proof_linked_to_fact(client):
    fact = _create_fact(client)
    proof = client.post(
        "/api/proofs",
        json={"type": "link", "title": "Dépôt GitHub", "fact_ids": [fact["id"]]},
    ).json()
    assert proof["fact_ids"] == [fact["id"]]
    assert client.get(f"/api/facts/{fact['id']}").json()["proof_ids"] == [proof["id"]]


def test_proof_unknown_fact_is_404(client):
    response = client.post(
        "/api/proofs",
        json={"type": "note", "title": "Orpheline",
              "fact_ids": ["00000000-0000-4000-8000-000000000000"]},
    )
    assert response.status_code == 404


def test_proof_relink_after_unlink(client):
    """Retirer puis remettre une liaison réactive la ligne (contrainte unique)."""
    fact = _create_fact(client)
    proof = client.post(
        "/api/proofs", json={"type": "note", "title": "Note", "fact_ids": [fact["id"]]}
    ).json()

    unlinked = client.patch(f"/api/proofs/{proof['id']}", json={"fact_ids": []}).json()
    assert unlinked["fact_ids"] == []

    relinked = client.patch(
        f"/api/proofs/{proof['id']}", json={"fact_ids": [fact["id"]]}
    ).json()
    assert relinked["fact_ids"] == [fact["id"]]


def test_proof_delete_hides_link_on_fact(client):
    fact = _create_fact(client)
    proof = client.post(
        "/api/proofs", json={"type": "note", "title": "Note", "fact_ids": [fact["id"]]}
    ).json()
    client.delete(f"/api/proofs/{proof['id']}")
    assert client.get(f"/api/facts/{fact['id']}").json()["proof_ids"] == []


# ---------------------------------------------------------------- offres

def test_offer_title_defaults_to_first_line(client):
    offer = client.post(
        "/api/offers",
        json={"raw_text": "Développeur Fullstack (H/F) - CDI\nReste de l'offre…"},
    ).json()
    assert offer["title"] == "Développeur Fullstack (H/F) - CDI"


def test_offer_soft_delete_excluded_from_list(client):
    offer = client.post("/api/offers", json={"raw_text": "Offre de test complète"}).json()
    assert client.delete(f"/api/offers/{offer['id']}").status_code == 204
    assert client.get(f"/api/offers/{offer['id']}").status_code == 404
    assert all(o["id"] != offer["id"] for o in client.get("/api/offers").json())
