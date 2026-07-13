"""Export PDF - fpdf2, format simple et parsable (exigence V1).

Les polices de base PDF sont limitées à latin-1 : les caractères hors champ
(œ, €, tirets typographiques...) sont translittérés plutôt que de faire échouer
l'export. Aucune dépendance système, aucun réseau.
"""

from __future__ import annotations

import re

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from sqlalchemy.orm import Session

from app.services.offer_service import get_offer
from app.services.variant_service import get_variant

# Clés en échappements \uXXXX : ces caractères viennent du texte COLLÉ par
# l'utilisateur et doivent être convertis pour survivre au latin-1 - mais la
# convention anti-tells les interdit en clair dans les sources.
_TRANSLITERATIONS = str.maketrans({
    "œ": "oe", "Œ": "OE", "æ": "ae", "Æ": "AE",
    "€": "EUR",
    "\u2026": "...",  # ellipse
    "\u2014": "-",  # tiret cadratin
    "\u2013": "-",  # demi-cadratin
    "\u2019": "'",  # apostrophe courbe fermante
    "\u2018": "'",  # apostrophe courbe ouvrante
    "\u201c": '"',  # guillemet courbe ouvrant
    "\u201d": '"',  # guillemet courbe fermant
    "\u2022": "-",  # puce
    "\u00a0": " ",  # espace insécable
    "\u202f": " ",  # espace fine insécable
})


def _latin1_safe(text: str) -> str:
    text = text.translate(_TRANSLITERATIONS)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _filename(title: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", _latin1_safe(title)).strip("-")[:60]
    return f"cv-adapte-{slug or 'offre'}.pdf"


def variant_pdf(session: Session, variant_id: str) -> tuple[bytes, str]:
    """Rend le texte « après » validé de la variante. Retourne (contenu, nom de fichier)."""
    variant = get_variant(session, variant_id)
    offer = get_offer(session, variant.offer_id)

    pdf = FPDF(format="A4")
    pdf.set_margins(20, 18, 20)
    pdf.set_auto_page_break(True, margin=18)
    pdf.add_page()
    pdf.set_font("helvetica", size=11)

    for line in (variant.adapted_text or "").replace("\r\n", "\n").split("\n"):
        if line.strip():
            # Sans new_x explicite, multi_cell laisse le curseur au bord droit
            # et la ligne suivante n'a plus de place (FPDFException).
            pdf.multi_cell(0, 5.5, _latin1_safe(line), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.ln(4)

    return bytes(pdf.output()), _filename(offer.title)
