"""Profil maître — V1 : un profil unique, créé au premier accès."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import MasterProfile
from app.schemas import MasterProfileUpdate


def get_or_create_profile(session: Session) -> MasterProfile:
    profile = session.scalars(
        select(MasterProfile)
        .where(MasterProfile.deleted_at.is_(None))
        .order_by(MasterProfile.created_at)
    ).first()
    if profile is None:
        profile = MasterProfile()
        session.add(profile)
        session.commit()
    return profile


def update_profile(session: Session, data: MasterProfileUpdate) -> MasterProfile:
    profile = get_or_create_profile(session)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    session.commit()
    return profile
