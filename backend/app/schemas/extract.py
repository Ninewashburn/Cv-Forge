"""Schéma de l'extraction de texte locale (« Importer un fichier »)."""

from pydantic import BaseModel


class ExtractedText(BaseModel):
    """Texte brut extrait d'un fichier (PDF ou texte), prêt à remplir un champ."""

    text: str
    filename: str
