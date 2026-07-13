"""Analyse d'offre et matching - sans LLM, 100 % local."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.db import Offer
from app.services import fact_service, keyword_engine, offer_service
from app.services.profile_service import get_or_create_profile


def analyze_offer(session: Session, offer_id: str) -> Offer:
    """(Re)calcule les mots-clés pondérés et les missions de l'offre."""
    offer = offer_service.get_offer(session, offer_id)
    offer.keywords = [list(kw) for kw in keyword_engine.extract_keywords(offer.raw_text)]
    offer.responsibilities = keyword_engine.extract_responsibilities(offer.raw_text)
    session.commit()
    return offer


def _ensure_analyzed(session: Session, offer_id: str) -> Offer:
    offer = offer_service.get_offer(session, offer_id)
    if not offer.keywords:
        offer = analyze_offer(session, offer_id)
    return offer


def profile_corpus(session: Session) -> str:
    """Le contenu du profil maître vu comme un texte matchable :
    en-tête + faits structurés + CV importé brut s'il existe."""
    profile = get_or_create_profile(session)
    parts = [profile.headline, profile.summary]
    for fact in fact_service.list_facts(session):
        parts.extend([fact.title, fact.content, " ".join(fact.tags or [])])
    if profile.raw_import_text:
        parts.append(profile.raw_import_text)
    return "\n".join(part for part in parts if part)


def match_offer(session: Session, offer_id: str, text: str | None = None) -> dict:
    """Couverture des mots-clés de l'offre par ``text`` (ou le profil maître)."""
    offer = _ensure_analyzed(session, offer_id)
    corpus = text.strip() if text and text.strip() else profile_corpus(session)
    result = keyword_engine.coverage(
        [tuple(kw) for kw in offer.keywords], corpus
    )
    missing = [r["keyword"] for r in result["results"] if not r["covered"]]
    return {"score": result["score"], "keywords": result["results"], "missing": missing}
