"""Génération tracée d'une variante de CV + validation anti-hallucination.

Chaque phrase générée provient d'un fait (``source_fact_ids``) et hérite de
ses preuves (``source_proof_ids``). La validation rejette toute phrase sans
source - règle produit non négociable, appliquée côté serveur.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import CvVariant, GeneratedSentence
from app.schemas import CvVariantUpdate
from app.services import fact_service, keyword_engine
from app.services.analysis_service import _ensure_analyzed
from app.services.errors import NotFoundError
from app.services.profile_service import get_or_create_profile

REJECTION_REASON_NO_SOURCE = "Sans source : aucune référence à un fait validé."


def validate_sentences(sentences: list[GeneratedSentence]) -> None:
    """Applique la règle anti-hallucination : pas de source > rejetée.

    Pose le statut explicitement (le default de colonne n'existe qu'au flush)."""
    for sentence in sentences:
        if not sentence.source_fact_ids:
            sentence.status = "rejected"
            sentence.reason = REJECTION_REASON_NO_SOURCE
        else:
            sentence.status = "valid"


def generate_variant(session: Session, offer_id: str) -> CvVariant:
    """Construit une variante à partir des faits couvrant les mots-clés de l'offre.

    Aucune invention : le titre recommandé est celui du profil (jamais un titre
    fabriqué), le résumé et les phrases ne réutilisent que des faits existants.
    """
    offer = _ensure_analyzed(session, offer_id)
    profile = get_or_create_profile(session)
    keywords = [tuple(kw) for kw in offer.keywords]

    selected = []
    for fact in fact_service.list_facts(session):
        fact_text = " ".join(
            [fact.title, fact.content, " ".join(fact.tags or [])]
        )
        result = keyword_engine.coverage(keywords, fact_text)
        if any(r["covered"] for r in result["results"]):
            selected.append(fact)

    variant = CvVariant(
        profile_id=profile.id,
        offer_id=offer.id,
        recommended_title=profile.headline,
        recommended_summary=" | ".join(fact.title for fact in selected),
    )
    session.add(variant)
    session.flush()

    for position, fact in enumerate(selected):
        variant.sentences.append(
            GeneratedSentence(
                text=fact.content.strip() or fact.title,
                source_fact_ids=[fact.id],
                source_proof_ids=fact.proof_ids,
                position=position,
            )
        )
    validate_sentences(variant.sentences)

    valid_texts = [s.text for s in variant.sentences if s.status == "valid"]
    variant.adapted_text = "\n".join(valid_texts)
    variant.match_score = keyword_engine.coverage(
        keywords, variant.adapted_text
    )["score"]

    session.commit()
    return variant


def create_manual_variant(session: Session, offer_id: str, adapted_text: str) -> CvVariant:
    """Variante portée par le wizard : le texte « après » a été validé ajout par
    ajout dans l'Avant/Après - il arrive donc déjà ``validated``."""
    offer = _ensure_analyzed(session, offer_id)
    profile = get_or_create_profile(session)
    keywords = [tuple(kw) for kw in offer.keywords]
    variant = CvVariant(
        profile_id=profile.id,
        offer_id=offer.id,
        recommended_title=profile.headline,
        adapted_text=adapted_text,
        match_score=keyword_engine.coverage(keywords, adapted_text)["score"],
        status="validated",
    )
    session.add(variant)
    session.commit()
    return variant


def list_variants_for_offer(session: Session, offer_id: str) -> list[CvVariant]:
    return list(
        session.scalars(
            select(CvVariant)
            .where(CvVariant.offer_id == offer_id, CvVariant.deleted_at.is_(None))
            .order_by(CvVariant.created_at)
        )
    )


def get_variant(session: Session, variant_id: str) -> CvVariant:
    variant = session.get(CvVariant, variant_id)
    if variant is None or variant.is_deleted:
        raise NotFoundError("variant", variant_id)
    return variant


def update_variant(session: Session, variant_id: str, data: CvVariantUpdate) -> CvVariant:
    variant = get_variant(session, variant_id)
    changes = data.model_dump(exclude_unset=True)
    if changes.get("status") is not None:
        changes["status"] = data.status.value
    for field, value in changes.items():
        setattr(variant, field, value)
    session.commit()
    return variant


def soft_delete_variant(session: Session, variant_id: str) -> None:
    variant = get_variant(session, variant_id)
    for sentence in variant.sentences:
        if sentence.deleted_at is None:
            sentence.soft_delete()
    variant.soft_delete()
    session.commit()
