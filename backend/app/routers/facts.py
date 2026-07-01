"""CRUD des faits du parcours."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.schemas import FactCreate, FactRead, FactUpdate
from app.services import fact_service

router = APIRouter(prefix="/api/facts", tags=["facts"])


@router.get("", response_model=list[FactRead])
def list_facts(session: Session = Depends(get_session)) -> list[FactRead]:
    return [FactRead.model_validate(f) for f in fact_service.list_facts(session)]


@router.post("", response_model=FactRead, status_code=201)
def create_fact(data: FactCreate, session: Session = Depends(get_session)) -> FactRead:
    return FactRead.model_validate(fact_service.create_fact(session, data))


@router.get("/{fact_id}", response_model=FactRead)
def get_fact(fact_id: str, session: Session = Depends(get_session)) -> FactRead:
    return FactRead.model_validate(fact_service.get_fact(session, fact_id))


@router.patch("/{fact_id}", response_model=FactRead)
def update_fact(
    fact_id: str, data: FactUpdate, session: Session = Depends(get_session)
) -> FactRead:
    return FactRead.model_validate(fact_service.update_fact(session, fact_id, data))


@router.delete("/{fact_id}", status_code=204)
def delete_fact(fact_id: str, session: Session = Depends(get_session)) -> None:
    fact_service.soft_delete_fact(session, fact_id)
