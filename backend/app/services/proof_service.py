"""Banque de preuves : CRUD + liaisons N–N vers les faits."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Proof, ProofFact
from app.schemas import ProofCreate, ProofUpdate
from app.services.errors import NotFoundError
from app.services.fact_service import get_fact


def list_proofs(session: Session) -> list[Proof]:
    return list(
        session.scalars(
            select(Proof).where(Proof.deleted_at.is_(None)).order_by(Proof.created_at)
        )
    )


def get_proof(session: Session, proof_id: str) -> Proof:
    proof = session.get(Proof, proof_id)
    if proof is None or proof.is_deleted:
        raise NotFoundError("proof", proof_id)
    return proof


def _set_fact_links(session: Session, proof: Proof, fact_ids: list[str]) -> None:
    """Aligne les liaisons sur ``fact_ids`` : soft-delete des retirées,
    réactivation des liaisons existantes (contrainte d'unicité), création du reste."""
    wanted = set(fact_ids)
    for fact_id in wanted:
        get_fact(session, fact_id)  # NotFoundError si le fait n'existe pas

    existing = {link.fact_id: link for link in proof.fact_links}
    for fact_id, link in existing.items():
        if fact_id in wanted and link.deleted_at is not None:
            link.deleted_at = None
        elif fact_id not in wanted and link.deleted_at is None:
            link.soft_delete()
    for fact_id in wanted - existing.keys():
        proof.fact_links.append(ProofFact(fact_id=fact_id))


def create_proof(session: Session, data: ProofCreate) -> Proof:
    proof = Proof(
        type=data.type.value,
        title=data.title,
        content=data.content,
        confidentiality=data.confidentiality.value,
    )
    session.add(proof)
    session.flush()  # attribue proof.id avant la création des liaisons
    _set_fact_links(session, proof, data.fact_ids)
    session.commit()
    return proof


def update_proof(session: Session, proof_id: str, data: ProofUpdate) -> Proof:
    proof = get_proof(session, proof_id)
    changes = data.model_dump(exclude_unset=True)
    fact_ids = changes.pop("fact_ids", None)
    for field in ("type", "confidentiality"):
        if changes.get(field) is not None:
            changes[field] = changes[field].value
    for field, value in changes.items():
        setattr(proof, field, value)
    if fact_ids is not None:
        _set_fact_links(session, proof, fact_ids)
    session.commit()
    return proof


def soft_delete_proof(session: Session, proof_id: str) -> None:
    proof = get_proof(session, proof_id)
    for link in proof.fact_links:
        if link.deleted_at is None:
            link.soft_delete()
    proof.soft_delete()
    session.commit()
