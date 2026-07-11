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
    response = _post(client, "cv.txt", "Développeur Angular — 5 ans".encode(), "text/plain")
    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Développeur Angular — 5 ans"
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
