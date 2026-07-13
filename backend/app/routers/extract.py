"""Extraction de texte locale - bouton « Importer un fichier » des zones du wizard."""

from fastapi import APIRouter, HTTPException, UploadFile

from app.schemas import ExtractedText
from app.services import extract_service

router = APIRouter(prefix="/api/extract", tags=["extract"])


@router.post("", response_model=ExtractedText)
async def extract(file: UploadFile) -> ExtractedText:
    """Texte brut d'un fichier PDF ou texte - extraction 100 % locale (pypdf).

    Endpoint générique unique pour les trois zones (offre, CV, profil LinkedIn) :
    le texte renvoyé atterrit dans le champ, éditable avant toute analyse."""
    content = await file.read()
    try:
        text = extract_service.extract_text(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ExtractedText(text=text, filename=file.filename or "fichier")
