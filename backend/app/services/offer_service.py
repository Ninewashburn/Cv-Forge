"""Offres d'emploi : CRUD (texte collé uniquement - aucun fetch réseau).

L'analyse (mots-clés, matching) arrive en Phase 2 avec les moteurs.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Offer
from app.schemas import OfferCreate, OfferUpdate
from app.services import keyword_engine
from app.services.errors import NotFoundError


def _default_title(raw_text: str) -> str:
    first_line = raw_text.strip().splitlines()[0] if raw_text.strip() else ""
    return first_line[:120]


def list_offers(session: Session) -> list[Offer]:
    return list(
        session.scalars(
            select(Offer).where(Offer.deleted_at.is_(None)).order_by(Offer.created_at)
        )
    )


def get_offer(session: Session, offer_id: str) -> Offer:
    offer = session.get(Offer, offer_id)
    if offer is None or offer.is_deleted:
        raise NotFoundError("offer", offer_id)
    return offer


def _apply_analysis(offer: Offer) -> None:
    offer.keywords = [
        list(kw) for kw in keyword_engine.extract_keywords(offer.raw_text)
    ]
    offer.responsibilities = keyword_engine.extract_responsibilities(offer.raw_text)


def create_offer(session: Session, data: OfferCreate) -> Offer:
    offer = Offer(
        raw_text=data.raw_text,
        title=data.title or _default_title(data.raw_text),
        company=data.company,
        source_url=data.source_url,
    )
    _apply_analysis(offer)
    session.add(offer)
    session.commit()
    return offer


def update_offer(session: Session, offer_id: str, data: OfferUpdate) -> Offer:
    offer = get_offer(session, offer_id)
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(offer, field, value)
    if "raw_text" in changes:
        _apply_analysis(offer)
    session.commit()
    return offer


def soft_delete_offer(session: Session, offer_id: str) -> None:
    offer = get_offer(session, offer_id)
    offer.soft_delete()
    session.commit()
