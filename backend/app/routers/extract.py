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
    # Taille annoncée vérifiée AVANT de lire : un mauvais clic sur un fichier
    # énorme ne doit pas remplir la mémoire pour finir refusé.
    if file.size is not None and file.size > extract_service.MAX_SIZE_BYTES:
        raise HTTPException(status_code=400, detail=extract_service.TOO_LARGE_MESSAGE)
    content = await file.read()
    try:
        text = extract_service.extract_text(file.filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ExtractedText(text=text, filename=file.filename or "fichier")
