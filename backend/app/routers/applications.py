"""Micro-suivi des candidatures : réponse ? entretien ? — 3 clics max."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.schemas import ApplicationCreate, ApplicationRead, ApplicationUpdate
from app.services import application_service

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationRead])
def list_applications(session: Session = Depends(get_session)) -> list[ApplicationRead]:
    return [
        ApplicationRead.model_validate(a)
        for a in application_service.list_applications(session)
    ]


@router.post("", response_model=ApplicationRead, status_code=201)
def create_application(
    data: ApplicationCreate, session: Session = Depends(get_session)
) -> ApplicationRead:
    return ApplicationRead.model_validate(
        application_service.create_application(session, data)
    )


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(
    application_id: str, session: Session = Depends(get_session)
) -> ApplicationRead:
    return ApplicationRead.model_validate(
        application_service.get_application(session, application_id)
    )


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: str, data: ApplicationUpdate, session: Session = Depends(get_session)
) -> ApplicationRead:
    return ApplicationRead.model_validate(
        application_service.update_application(session, application_id, data)
    )


@router.delete("/{application_id}", status_code=204)
def delete_application(application_id: str, session: Session = Depends(get_session)) -> None:
    application_service.soft_delete_application(session, application_id)
