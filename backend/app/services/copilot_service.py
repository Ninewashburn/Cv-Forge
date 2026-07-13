"""Mode copilote - bibliothèque de prompts verrouillés.

Quatre intentions (spec canonique : ``docs/specs/copilot_prompts.md``), un
pattern commun : **ce qui manque n'est jamais ajouté**, il est listé « À
compléter par le candidat ». ADAPTER est le défaut ; son retour passe
obligatoirement par l'Avant/Après.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.schemas import PromptKind
from app.services.analysis_service import match_offer, profile_corpus
from app.services.offer_service import get_offer
from app.services.profile_service import get_or_create_profile

ADAPTER_TEMPLATE = """Tu es un assistant de candidature. RÈGLES ABSOLUES, sans exception :
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

AUDITER_TEMPLATE = """Tu es un recruteur exigeant pour le poste ci-dessous. Analyse ce CV avec une honnêteté brutale. RÈGLES :
1. Tu critiques, tu ne réécris RIEN.
2. Pointe : formulations faibles, mots creux (dynamique, motivé, passionné...), affirmations sans preuve, sections mal hiérarchisées.
3. Pour chaque faiblesse : cite le passage exact, explique pourquoi ça affaiblit, et pose la question qui permettrait de le renforcer AVEC UN FAIT RÉEL.
4. Ne suggère JAMAIS d'ajouter une compétence, un chiffre ou une expérience absente du CV.

=== OFFRE D'EMPLOI ===
{offer_text}

=== CV ===
{cv_text}"""

MUSCLER_TEMPLATE = """Reformule les expériences de ce CV pour les rendre plus percutantes. RÈGLES :
1. Verbes d'action, résultat en tête de phrase - UNIQUEMENT à partir des faits déjà présents dans le CV.
2. INTERDIT d'ajouter un chiffre, un pourcentage ou un résultat absent du CV. Si une réalisation gagnerait à être chiffrée, ne l'invente pas : liste-la dans « À chiffrer par le candidat » à la fin.
3. Pas de superlatifs, pas de mots creux.

Réponds en deux blocs : d'abord le CV reformulé seul, puis « À chiffrer par le candidat ».

=== CV - SOURCE DE VÉRITÉ UNIQUE ===
{cv_text}"""

ACCROCHER_TEMPLATE = """Rédige une accroche de 3 lignes maximum pour ce CV, ciblée sur cette offre. RÈGLES :
1. Uniquement des faits du CV.
2. Interdit « passionné par » et les adjectifs autoproclamés (dynamique, motivé, rigoureux).
3. Que du vérifiable : années d'expérience réelles, technos réelles, réalisations réelles.

=== OFFRE D'EMPLOI ===
{offer_text}

=== CV ===
{cv_text}"""

_TEMPLATES: dict[PromptKind, str] = {
    PromptKind.ADAPTER: ADAPTER_TEMPLATE,
    PromptKind.AUDITER: AUDITER_TEMPLATE,
    PromptKind.MUSCLER: MUSCLER_TEMPLATE,
    PromptKind.ACCROCHER: ACCROCHER_TEMPLATE,
}


def build_prompt(
    session: Session,
    offer_id: str,
    text: str | None = None,
    kind: PromptKind = PromptKind.ADAPTER,
) -> dict:
    offer = get_offer(session, offer_id)
    profile = get_or_create_profile(session)
    cv_text = (text or "").strip() or (profile.raw_import_text or "").strip()
    if not cv_text:
        cv_text = profile_corpus(session)

    matching = match_offer(session, offer_id, cv_text)
    missing = matching["missing"]
    prompt = _TEMPLATES[kind].format(
        offer_text=offer.raw_text,
        cv_text=cv_text,
        missing=", ".join(missing) if missing else "(aucun)",
    )
    return {"prompt": prompt, "missing_keywords": missing}
