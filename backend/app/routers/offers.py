"""Offres d'emploi : CRUD (texte collé uniquement) + analyse, matching, copilote."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.schemas import (
    CopilotPromptRead,
    CopilotPromptRequest,
    CvVariantRead,
    MatchingResult,
    MatchRequest,
    OfferCreate,
    OfferRead,
    OfferUpdate,
)
from app.services import analysis_service, copilot_service, offer_service, variant_service

router = APIRouter(prefix="/api/offers", tags=["offers"])


@router.get("", response_model=list[OfferRead])
def list_offers(session: Session = Depends(get_session)) -> list[OfferRead]:
    return [OfferRead.model_validate(o) for o in offer_service.list_offers(session)]


@router.post("", response_model=OfferRead, status_code=201)
def create_offer(data: OfferCreate, session: Session = Depends(get_session)) -> OfferRead:
    return OfferRead.model_validate(offer_service.create_offer(session, data))


@router.get("/{offer_id}", response_model=OfferRead)
def get_offer(offer_id: str, session: Session = Depends(get_session)) -> OfferRead:
    return OfferRead.model_validate(offer_service.get_offer(session, offer_id))


@router.patch("/{offer_id}", response_model=OfferRead)
def update_offer(
    offer_id: str, data: OfferUpdate, session: Session = Depends(get_session)
) -> OfferRead:
    return OfferRead.model_validate(offer_service.update_offer(session, offer_id, data))


@router.delete("/{offer_id}", status_code=204)
def delete_offer(offer_id: str, session: Session = Depends(get_session)) -> None:
    offer_service.soft_delete_offer(session, offer_id)


@router.post("/{offer_id}/analyze", response_model=OfferRead)
def analyze_offer(offer_id: str, session: Session = Depends(get_session)) -> OfferRead:
    """Recalcule mots-clés pondérés et missions de l'offre (sans LLM)."""
    return OfferRead.model_validate(analysis_service.analyze_offer(session, offer_id))


@router.post("/{offer_id}/matching", response_model=MatchingResult)
def match_offer(
    offer_id: str, data: MatchRequest, session: Session = Depends(get_session)
) -> MatchingResult:
    """Couverture des mots-clés par le texte fourni, ou par le profil maître."""
    return MatchingResult.model_validate(
        analysis_service.match_offer(session, offer_id, data.text)
    )


@router.post("/{offer_id}/copilot-prompt", response_model=CopilotPromptRead)
def copilot_prompt(
    offer_id: str, data: CopilotPromptRequest, session: Session = Depends(get_session)
) -> CopilotPromptRead:
    """Prompt verrouillé (anti-hallucination) à coller dans le chat de l'utilisateur.

    ``kind`` choisit l'intention : adapter (défaut) / auditer / muscler / accrocher."""
    return CopilotPromptRead.model_validate(
        copilot_service.build_prompt(session, offer_id, data.text, data.kind)
    )


@router.post("/{offer_id}/variants", response_model=CvVariantRead, status_code=201)
def generate_variant(offer_id: str, session: Session = Depends(get_session)) -> CvVariantRead:
    """Génère une variante tracée : chaque phrase référence ses faits et preuves."""
    return CvVariantRead.model_validate(variant_service.generate_variant(session, offer_id))


@router.get("/{offer_id}/variants", response_model=list[CvVariantRead])
def list_variants(offer_id: str, session: Session = Depends(get_session)) -> list[CvVariantRead]:
    return [
        CvVariantRead.model_validate(v)
        for v in variant_service.list_variants_for_offer(session, offer_id)
    ]
