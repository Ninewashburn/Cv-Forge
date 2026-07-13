"""Micro-suivi des candidatures - l'instrument de mesure du MVP statement."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Application
from app.schemas import ApplicationCreate, ApplicationUpdate
from app.services.errors import NotFoundError
from app.services.offer_service import get_offer
from app.services.variant_service import get_variant


def list_applications(session: Session) -> list[Application]:
    return list(
        session.scalars(
            select(Application)
            .where(Application.deleted_at.is_(None))
            .order_by(Application.sent_at.desc())
        )
    )


def get_application(session: Session, application_id: str) -> Application:
    application = session.get(Application, application_id)
    if application is None or application.is_deleted:
        raise NotFoundError("application", application_id)
    return application


def create_application(session: Session, data: ApplicationCreate) -> Application:
    get_offer(session, data.offer_id)  # NotFoundError si l'offre n'existe pas
    if data.variant_id is not None:
        get_variant(session, data.variant_id)
    application = Application(
        offer_id=data.offer_id,
        variant_id=data.variant_id,
        notes=data.notes,
    )
    session.add(application)
    session.commit()
    return application


def update_application(
    session: Session, application_id: str, data: ApplicationUpdate
) -> Application:
    application = get_application(session, application_id)
    changes = data.model_dump(exclude_unset=True)
    if changes.get("status") is not None:
        changes["status"] = data.status.value
    for field, value in changes.items():
        setattr(application, field, value)
    session.commit()
    return application


def soft_delete_application(session: Session, application_id: str) -> None:
    application = get_application(session, application_id)
    application.soft_delete()
    session.commit()
