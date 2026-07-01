"""Mode copilote — prompt verrouillé, porté du prototype Lite.

Règles anti-hallucination imposées dans le prompt lui-même : l'IA de
l'utilisateur ne peut que reformuler / réorganiser / prioriser le CV fourni,
et les mots-clés absents lui sont explicitement interdits d'ajout.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.analysis_service import match_offer, profile_corpus
from app.services.offer_service import get_offer
from app.services.profile_service import get_or_create_profile

PROMPT_TEMPLATE = """Tu es un assistant de candidature. RÈGLES ABSOLUES, sans exception :
1. Tu n'inventes JAMAIS : aucune compétence, expérience, diplôme, certification, technologie ou chiffre absent du CV ci-dessous.
2. Tu peux uniquement reformuler, réorganiser, prioriser et résumer le contenu du CV.
3. Les mots-clés listés en bas sont ABSENTS du CV : ne les ajoute PAS. Liste-les à la fin sous le titre « À vérifier avec le candidat ».
4. Conserve la langue, le ton factuel et la structure générale du CV.
5. Mets en avant en priorité ce qui correspond à l'offre.

Réponds en deux blocs : d'abord le CV adapté seul, puis la liste « À vérifier avec le candidat ».

=== OFFRE D'EMPLOI ===
{offer_text}

=== CV - SOURCE DE VÉRITÉ UNIQUE ===
{cv_text}

=== MOTS-CLÉS DE L'OFFRE ABSENTS DU CV (NE PAS AJOUTER) ===
{missing}"""


def build_prompt(session: Session, offer_id: str, text: str | None = None) -> dict:
    offer = get_offer(session, offer_id)
    profile = get_or_create_profile(session)
    cv_text = (text or "").strip() or (profile.raw_import_text or "").strip()
    if not cv_text:
        cv_text = profile_corpus(session)

    matching = match_offer(session, offer_id, cv_text)
    missing = matching["missing"]
    prompt = PROMPT_TEMPLATE.format(
        offer_text=offer.raw_text,
        cv_text=cv_text,
        missing=", ".join(missing) if missing else "(aucun)",
    )
    return {"prompt": prompt, "missing_keywords": missing}
