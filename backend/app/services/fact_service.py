"""Faits du parcours : CRUD avec soft delete."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Fact
from app.schemas import FactCreate, FactUpdate
from app.services.errors import NotFoundError
from app.services.profile_service import get_or_create_profile


def list_facts(session: Session) -> list[Fact]:
    return list(
        session.scalars(
            select(Fact)
            .where(Fact.deleted_at.is_(None))
            .order_by(Fact.position, Fact.created_at)
        )
    )


def get_fact(session: Session, fact_id: str) -> Fact:
    fact = session.get(Fact, fact_id)
    if fact is None or fact.is_deleted:
        raise NotFoundError("fact", fact_id)
    return fact


def create_fact(session: Session, data: FactCreate) -> Fact:
    profile_id = data.profile_id or get_or_create_profile(session).id
    fact = Fact(
        profile_id=profile_id,
        type=data.type.value,
        title=data.title,
        content=data.content,
        tags=data.tags,
        validated=data.validated,
        position=data.position,
    )
    session.add(fact)
    session.commit()
    return fact


def update_fact(session: Session, fact_id: str, data: FactUpdate) -> Fact:
    fact = get_fact(session, fact_id)
    changes = data.model_dump(exclude_unset=True)
    if "type" in changes and changes["type"] is not None:
        changes["type"] = data.type.value
    for field, value in changes.items():
        setattr(fact, field, value)
    session.commit()
    return fact


def soft_delete_fact(session: Session, fact_id: str) -> None:
    fact = get_fact(session, fact_id)
    for link in fact.proof_links:
        if link.deleted_at is None:
            link.soft_delete()
    fact.soft_delete()
    session.commit()
