"""Tests API des moteurs : analyse, matching, copilote, variantes tracées."""

OFFER_TEXT = """Développeur Fullstack Angular / Spring Boot (H/F) - CDI, Caen
Vos missions :
- Développer de nouvelles fonctionnalités en Angular et TypeScript
- Concevoir des API en Spring Boot avec PostgreSQL
- Déployer avec Docker, Kubernetes et GitLab CI
Vous maîtrisez Angular, Spring Boot et PostgreSQL.
Angular et Spring Boot sont au coeur de notre stack."""

CV_TEXT = """Développeuse fullstack
- Dashboard de supervision en Angular et TypeScript
- API REST en Spring Boot, base PostgreSQL, conteneurisation Docker"""


def _create_offer(client):
    return client.post("/api/offers", json={"raw_text": OFFER_TEXT}).json()


def _create_fact(client, title, content="", tags=None):
    return client.post(
        "/api/facts",
        json={"type": "skill", "title": title, "content": content, "tags": tags or []},
    ).json()


# ------------------------------------------------------------- analyse

def test_offer_is_analyzed_on_creation(client):
    offer = _create_offer(client)
    keywords = dict(map(tuple, offer["keywords"]))
    assert "spring boot" in keywords
    assert offer["responsibilities"]


def test_editing_raw_text_reanalyzes(client):
    offer = _create_offer(client)
    updated = client.patch(
        f"/api/offers/{offer['id']}",
        json={"raw_text": "Assistant de gestion. Facturation et devis. Facturation clients."},
    ).json()
    keywords = dict(map(tuple, updated["keywords"]))
    assert "facturation" in keywords
    assert "spring boot" not in keywords


# ------------------------------------------------------------- matching

def test_matching_against_free_text(client):
    offer = _create_offer(client)
    result = client.post(
        f"/api/offers/{offer['id']}/matching", json={"text": CV_TEXT}
    ).json()
    assert 0 < result["score"] < 100
    assert "kubernetes" in result["missing"]
    covered = {k["keyword"] for k in result["keywords"] if k["covered"]}
    assert "angular" in covered


def test_matching_against_master_profile(client):
    offer = _create_offer(client)
    _create_fact(client, "Angular", "Dashboard de supervision", ["angular", "typescript"])
    result = client.post(f"/api/offers/{offer['id']}/matching", json={}).json()
    covered = {k["keyword"] for k in result["keywords"] if k["covered"]}
    assert "angular" in covered


# ------------------------------------------------------------- copilote

def test_copilot_prompt_is_locked_and_complete(client):
    offer = _create_offer(client)
    body = client.post(
        f"/api/offers/{offer['id']}/copilot-prompt", json={"text": CV_TEXT}
    ).json()
    prompt = body["prompt"]
    assert "Tu n'inventes JAMAIS" in prompt  # kind absent → ADAPTER par défaut
    assert OFFER_TEXT in prompt
    assert CV_TEXT in prompt
    assert "kubernetes" in body["missing_keywords"]
    # Les mots-clés manquants sont explicitement interdits d'ajout.
    assert "NE PAS AJOUTER" in prompt


def test_copilot_prompt_library_intents(client):
    """Bibliothèque de prompts verrouillés : chaque intention garde son verrou."""
    offer = _create_offer(client)
    url = f"/api/offers/{offer['id']}/copilot-prompt"

    auditer = client.post(url, json={"text": CV_TEXT, "kind": "auditer"}).json()["prompt"]
    assert "tu ne réécris RIEN" in auditer
    assert "Ne suggère JAMAIS" in auditer
    assert OFFER_TEXT in auditer and CV_TEXT in auditer

    muscler = client.post(url, json={"text": CV_TEXT, "kind": "muscler"}).json()["prompt"]
    assert "À chiffrer par le candidat" in muscler
    assert "INTERDIT d'ajouter un chiffre" in muscler
    assert CV_TEXT in muscler
    assert OFFER_TEXT not in muscler  # MUSCLER travaille sur le CV seul

    accrocher = client.post(url, json={"text": CV_TEXT, "kind": "accrocher"}).json()["prompt"]
    assert "3 lignes maximum" in accrocher
    assert "passionné par" in accrocher  # cité comme interdit
    assert OFFER_TEXT in accrocher and CV_TEXT in accrocher


def test_copilot_prompt_rejects_unknown_kind(client):
    offer = _create_offer(client)
    response = client.post(
        f"/api/offers/{offer['id']}/copilot-prompt",
        json={"text": CV_TEXT, "kind": "ats-boost"},
    )
    assert response.status_code == 422  # intention hors bibliothèque → refusée


# ------------------------------------------------------------- variantes

def test_variant_generation_is_traced(client):
    offer = _create_offer(client)
    fact = _create_fact(
        client, "Angular", "Dashboard de supervision en Angular", ["angular"]
    )
    proof = client.post(
        "/api/proofs",
        json={"type": "link", "title": "Dépôt", "fact_ids": [fact["id"]]},
    ).json()

    variant = client.post(f"/api/offers/{offer['id']}/variants").json()
    assert variant["offer_id"] == offer["id"]
    assert variant["match_score"] > 0
    assert "Dashboard de supervision" in variant["adapted_text"]
    assert len(variant["sentences"]) == 1

    sentence = variant["sentences"][0]
    assert sentence["source_fact_ids"] == [fact["id"]]
    assert sentence["source_proof_ids"] == [proof["id"]]
    assert sentence["status"] == "valid"


def test_variant_excludes_unrelated_facts(client):
    offer = _create_offer(client)
    _create_fact(client, "Angular", tags=["angular"])
    _create_fact(client, "Pâtisserie", "CAP pâtissier", ["patisserie"])

    variant = client.post(f"/api/offers/{offer['id']}/variants").json()
    texts = [s["text"] for s in variant["sentences"]]
    assert not any("pâtissier" in t.lower() for t in texts)


def test_variant_title_is_profile_headline_never_invented(client):
    client.put("/api/profile", json={"headline": "Développeuse Fullstack"})
    offer = _create_offer(client)
    variant = client.post(f"/api/offers/{offer['id']}/variants").json()
    assert variant["recommended_title"] == "Développeuse Fullstack"


def test_variant_update_and_delete(client):
    offer = _create_offer(client)
    variant = client.post(f"/api/offers/{offer['id']}/variants").json()

    patched = client.patch(
        f"/api/variants/{variant['id']}",
        json={"adapted_text": "Mon CV adapté", "status": "validated"},
    ).json()
    assert patched["adapted_text"] == "Mon CV adapté"
    assert patched["status"] == "validated"

    assert client.delete(f"/api/variants/{variant['id']}").status_code == 204
    assert client.get(f"/api/variants/{variant['id']}").status_code == 404
    assert client.get(f"/api/offers/{offer['id']}/variants").json() == []
