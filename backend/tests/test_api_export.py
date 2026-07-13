"""Tests Bloc 3 : variante manuelle, export PDF, micro-suivi."""


def _create_offer(client, raw_text="Offre de test Angular pour export complet"):
    return client.post("/api/offers", json={"raw_text": raw_text}).json()


# Lignes consécutives SANS ligne vide : c'est le cas qui piégeait multi_cell
# (curseur laissé au bord droit) - une ligne vide masquait le bug via ln().
_DEFAULT_TEXT = "Mon CV adapté et validé.\nExpérience Angular.\nLigne trois."


def _manual_variant(client, offer_id, text=_DEFAULT_TEXT):
    response = client.post(f"/api/offers/{offer_id}/variants", json={"adapted_text": text})
    assert response.status_code == 201
    return response.json()


# ------------------------------------------------------- variante manuelle

def test_manual_variant_carries_wizard_text(client):
    offer = _create_offer(client)
    variant = _manual_variant(client, offer["id"])
    assert variant["adapted_text"].startswith("Mon CV adapté")
    assert variant["status"] == "validated"  # ajouts déjà confirmés dans l'Avant/Après
    assert variant["match_score"] is not None
    assert variant["sentences"] == []  # pas de génération depuis les faits


def test_variant_generation_without_body_still_works(client):
    offer = _create_offer(client)
    response = client.post(f"/api/offers/{offer['id']}/variants")
    assert response.status_code == 201
    assert response.json()["status"] == "draft"


# ------------------------------------------------------------- export PDF

def test_variant_pdf_is_downloadable(client):
    offer = _create_offer(client, "Développeur Angular (H/F) - CDI")
    variant = _manual_variant(client, offer["id"])
    response = client.get(f"/api/variants/{variant['id']}/pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert "cv-adapte-" in response.headers["content-disposition"]
    assert response.content.startswith(b"%PDF")


def test_pdf_survives_non_latin1_characters(client):
    offer = _create_offer(client)
    # Caractères en \uXXXX (convention anti-tells) : ce sont des ENTRÉES de test,
    # elles simulent du texte collé par l'utilisateur avec typographie riche.
    variant = _manual_variant(
        client,
        offer["id"],
        "Cœur d'œuvre \u2014 budget 10 000 €\u2026 \u201cprojet\u201d ★",
    )
    response = client.get(f"/api/variants/{variant['id']}/pdf")
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")


def test_pdf_of_unknown_variant_is_404(client):
    assert client.get("/api/variants/00000000-0000-4000-8000-000000000000/pdf").status_code == 404


# ------------------------------------------------------------ micro-suivi

def test_application_lifecycle(client):
    offer = _create_offer(client)
    variant = _manual_variant(client, offer["id"])

    created = client.post(
        "/api/applications", json={"offer_id": offer["id"], "variant_id": variant["id"]}
    )
    assert created.status_code == 201
    application = created.json()
    assert application["status"] == "envoyee"
    assert application["sent_at"]

    patched = client.patch(
        f"/api/applications/{application['id']}", json={"status": "entretien"}
    ).json()
    assert patched["status"] == "entretien"

    listed = client.get("/api/applications").json()
    assert [a["id"] for a in listed] == [application["id"]]

    assert client.delete(f"/api/applications/{application['id']}").status_code == 204
    assert client.get("/api/applications").json() == []


def test_application_unknown_offer_is_404(client):
    response = client.post(
        "/api/applications",
        json={"offer_id": "00000000-0000-4000-8000-000000000000"},
    )
    assert response.status_code == 404
