"""Tests de l'extraction de texte locale (« Importer un fichier »)."""

from fpdf import FPDF
from fpdf.enums import XPos, YPos

from app.services.extract_service import extract_text


def _pdf_bytes(*lines: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)
    for line in lines:
        pdf.multi_cell(0, 8, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    return bytes(pdf.output())


def _post(client, filename: str, content: bytes, content_type: str = "application/octet-stream"):
    return client.post("/api/extract", files={"file": (filename, content, content_type)})


def test_txt_utf8_roundtrip(client):
    response = _post(client, "cv.txt", "Développeur Angular - 5 ans".encode(), "text/plain")
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Développeur Angular - 5 ans"
    assert body["filename"] == "cv.txt"


def test_txt_cp1252_fallback(client):
    # Bloc-notes Windows historique : « é » = 0xE9, invalide en UTF-8.
    response = _post(client, "cv.txt", b"D\xe9veloppeur", "text/plain")
    assert response.status_code == 200
    assert response.json()["text"] == "Développeur"


def test_pdf_extraction(client):
    content = _pdf_bytes("Développeur Python", "Angular et FastAPI")
    response = _post(client, "cv.pdf", content, "application/pdf")
    assert response.status_code == 200
    text = response.json()["text"]
    assert "Développeur Python" in text
    assert "Angular et FastAPI" in text


def test_pdf_signature_wins_over_txt_extension(client):
    # Un vrai PDF mal renommé en .txt doit quand même passer par pypdf.
    response = _post(client, "offre.txt", _pdf_bytes("Offre Michelin"), "text/plain")
    assert response.status_code == 200
    assert "Offre Michelin" in response.json()["text"]


def test_rejects_unsupported_format(client):
    response = _post(client, "photo.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 20, "image/png")
    assert response.status_code == 400
    assert "copier-coller" in response.json()["detail"].lower()


def test_rejects_fake_pdf(client):
    response = _post(client, "cv.pdf", b"pas un pdf", "application/pdf")
    assert response.status_code == 400


def test_rejects_empty_file(client):
    response = _post(client, "cv.txt", b"", "text/plain")
    assert response.status_code == 400


# ------------------------------------ PDF « lettres détachées » (Canva, test réel)


def test_repair_exploded_text_rebuilds_words():
    from app.services.extract_service import _repair_exploded_text

    exploded = "E x p é r i e n c e s\nS e n s  d u  s e r v i c e\nE s p r i t  d ' é q u i p e"
    assert _repair_exploded_text(exploded) == "Expériences\nSens du service\nEsprit d'équipe"


def test_repair_leaves_normal_text_untouched():
    from app.services.extract_service import _repair_exploded_text

    normal = "Développeur full stack avec plusieurs années d'expérience.\nAngular, Java et SQL."
    assert _repair_exploded_text(normal) == normal


def test_pdf_exploded_words_are_repaired(client):
    content = _pdf_bytes(
        "P r é p a r a t i o n  d e s  c o m m a n d e s",
        "R e l a t i o n  c l i e n t  e t  s e r v i c e",
    )
    response = _post(client, "canva.pdf", content, "application/pdf")
    assert response.status_code == 200
    text = response.json()["text"]
    assert "Préparation des commandes" in text
    assert "Relation client et service" in text


def test_pdf_fully_exploded_gets_honest_error(client):
    # Deux lettres par ligne : la réparation ligne à ligne ne s'applique pas
    # (moins de 4 mots), le détecteur global doit alors refuser honnêtement.
    lines = [f"{a} {b}" for a, b in zip("abcdefghijklm", "nopqrstuvwxyz")]
    response = _post(client, "canva.pdf", _pdf_bytes(*lines), "application/pdf")
    assert response.status_code == 400
    assert "mise en page" in response.json()["detail"]


def test_rejects_pdf_without_text(client):
    # Page vide = même symptôme qu'un document scanné en image.
    response = _post(client, "scan.pdf", _pdf_bytes(), "application/pdf")
    assert response.status_code == 400
    assert "scanné" in response.json()["detail"]


def test_tidy_normalizes_line_endings_and_blank_runs():
    text = extract_text("cv.txt", b"Ligne 1\r\n\r\n\r\n\r\nLigne 2\r\n")
    assert text == "Ligne 1\n\nLigne 2"


def test_rejects_binary_masquerading_as_txt():
    try:
        extract_text("cv.txt", b"abc\x00def")
    except ValueError as exc:
        assert "texte lisible" in str(exc)
    else:
        raise AssertionError("un fichier binaire déguisé en .txt doit être refusé")
