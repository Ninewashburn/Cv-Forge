"""Extraction de texte locale (PDF, texte brut) - le fichier ne quitte jamais la machine.

Sert le bouton « Importer un fichier » des trois zones du wizard (offre, CV,
profil LinkedIn). Un seul point d'entrée générique : ``extract_text``. Le texte
extrait est renvoyé tel quel au champ, visible et éditable avant toute analyse -
même contrat que le copier-coller, qui reste le fallback universel.
"""

from __future__ import annotations

import re
from io import BytesIO

from pypdf import PdfReader

# Garde-fou local : au-delà, c'est presque sûrement un scan image ou un mauvais fichier.
MAX_SIZE_BYTES = 20 * 1024 * 1024

_TEXT_EXTENSIONS = (".txt", ".text", ".md")

_FALLBACK_HINT = "Le copier-coller reste toujours possible."


def extract_text(filename: str | None, content: bytes) -> str:
    """Texte brut d'un fichier PDF ou texte. Lève ``ValueError`` (message utilisateur) sinon."""
    if not content:
        raise ValueError(f"Ce fichier est vide. {_FALLBACK_HINT}")
    if len(content) > MAX_SIZE_BYTES:
        raise ValueError(
            f"Fichier trop volumineux (20 Mo maximum). {_FALLBACK_HINT}"
        )

    name = (filename or "").lower()
    # Signature avant extension : un « offre.txt » qui est en réalité un PDF marche quand même.
    if b"%PDF" in content[:1024]:
        return _from_pdf(content)
    if name.endswith(".pdf"):
        raise ValueError(f"Ce fichier n'est pas un vrai PDF. {_FALLBACK_HINT}")
    if name.endswith(_TEXT_EXTENSIONS) or not name:
        return _from_plain_text(content)
    raise ValueError(
        f"Format non pris en charge - PDF ou fichier texte (.txt). {_FALLBACK_HINT}"
    )


def _from_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted:
            # Certains PDF sont « chiffrés » avec un mot de passe vide (protection copie).
            try:
                reader.decrypt("")
            except Exception as exc:  # noqa: BLE001 - pypdf lève des types variés ici
                raise ValueError(
                    "Ce PDF est protégé par mot de passe - déverrouille-le d'abord. "
                    + _FALLBACK_HINT
                ) from exc
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001 - tout PDF cassé = message utilisateur
        raise ValueError(f"Ce PDF est illisible ou corrompu. {_FALLBACK_HINT}") from exc

    text = _tidy("\n\n".join(p for p in pages if p))
    if not text:
        raise ValueError(
            "Aucun texte trouvé dans ce PDF - c'est probablement un document scanné "
            f"(image). {_FALLBACK_HINT}"
        )
    text = _repair_exploded_text(text)
    if _looks_exploded(text):
        raise ValueError(
            "Ce PDF a une mise en page qui complique l'extraction du texte "
            f"(chaque lettre posée séparément). {_FALLBACK_HINT}"
        )
    return text


def _from_plain_text(content: bytes) -> str:
    if b"\x00" in content:
        raise ValueError(
            f"Ce fichier n'est pas du texte lisible. {_FALLBACK_HINT}"
        )
    try:
        raw = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        # Fichiers Windows français typiques (Bloc-notes historique).
        raw = content.decode("cp1252", errors="replace")
    text = _tidy(raw)
    if not text:
        raise ValueError(f"Ce fichier est vide. {_FALLBACK_HINT}")
    return text


def _repair_exploded_text(text: str) -> str:
    """Répare les PDF (Canva, Figma...) qui posent chaque lettre séparément :
    « E x p é r i e n c e s » redevient « Expériences ».

    Une ligne est jugée éclatée quand l'essentiel de ses « mots » font un seul
    caractère ; les groupes séparés par 2 espaces ou plus sont les vrais mots.
    Les lignes normales ne sont jamais touchées (accents compris)."""
    repaired = []
    for line in text.split("\n"):
        tokens = line.split()
        singles = sum(1 for token in tokens if len(token) == 1)
        if len(tokens) >= 4 and singles / len(tokens) > 0.6:
            segments = re.split(r"\s{2,}", line.strip())
            line = " ".join("".join(segment.split()) for segment in segments)
        repaired.append(line)
    return "\n".join(repaired)


def _looks_exploded(text: str) -> bool:
    """Vrai si, même après réparation, le texte reste en lettres détachées."""
    tokens = text.split()
    if len(tokens) < 20:
        return False
    singles = sum(1 for token in tokens if len(token) == 1)
    return singles / len(tokens) > 0.5


def _tidy(text: str) -> str:
    """Nettoyage léger : fins de ligne uniformes, pas plus d'une ligne vide d'affilée."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", text).strip()
