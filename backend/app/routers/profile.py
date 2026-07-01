"""Profil maître : un seul profil en V1, créé au premier accès."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.schemas import MasterProfileRead, MasterProfileUpdate
from app.services import profile_service

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("", response_model=MasterProfileRead)
def get_profile(session: Session = Depends(get_session)) -> MasterProfileRead:
    return MasterProfileRead.model_validate(profile_service.get_or_create_profile(session))


@router.put("", response_model=MasterProfileRead)
def update_profile(
    data: MasterProfileUpdate, session: Session = Depends(get_session)
) -> MasterProfileRead:
    return MasterProfileRead.model_validate(profile_service.update_profile(session, data))
