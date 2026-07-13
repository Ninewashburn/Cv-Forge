"""Banque de preuves : CRUD + liaisons N-N vers les faits + pièce jointe locale."""

from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import resolve_data_dir
from app.db import Proof, ProofFact
from app.schemas import ProofCreate, ProofUpdate
from app.services.errors import NotFoundError
from app.services.fact_service import get_fact

# Pièces jointes rangées sous <data>/proofs/ - le backup ZIP les embarque déjà.
PROOFS_DIR_NAME = "proofs"
MAX_FILE_BYTES = 25 * 1024 * 1024


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
    # La pièce jointe éventuelle reste sur disque : soft delete = récupérable.


def attach_file(session: Session, proof_id: str, filename: str, content: bytes) -> Proof:
    """Range la pièce jointe sous <data>/proofs/ et la référence sur la preuve.

    Une seule pièce par preuve : en remettre une remplace la précédente
    (geste explicite de l'utilisateur, comme réécrire le contenu d'une note)."""
    proof = get_proof(session, proof_id)
    if not content:
        raise ValueError("Ce fichier est vide.")
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("Fichier trop volumineux (25 Mo maximum).")

    proofs_dir = resolve_data_dir() / PROOFS_DIR_NAME
    proofs_dir.mkdir(parents=True, exist_ok=True)
    stored = f"{proof.id}--{_safe_filename(filename)}"

    if proof.file_name:
        _existing_path(proof).unlink(missing_ok=True)
    (proofs_dir / stored).write_bytes(content)
    proof.file_name = f"{PROOFS_DIR_NAME}/{stored}"
    session.commit()
    return proof


def attached_file(session: Session, proof_id: str) -> tuple[Path, str]:
    """(chemin, nom d'origine) de la pièce jointe. NotFoundError si absente."""
    proof = get_proof(session, proof_id)
    if not proof.file_name:
        raise NotFoundError("proof file", proof_id)
    path = _existing_path(proof)
    if not path.is_file():
        raise NotFoundError("proof file", proof_id)
    display = path.name.split("--", 1)[-1]
    return path, display


def _existing_path(proof: Proof) -> Path:
    """Chemin absolu de la pièce référencée, verrouillé dans le dossier de données."""
    data_dir = resolve_data_dir().resolve()
    path = (data_dir / str(proof.file_name)).resolve()
    if not path.is_relative_to(data_dir):  # garde-fou path traversal
        raise NotFoundError("proof file", proof.id)
    return path


def _safe_filename(raw: str) -> str:
    """Nom de fichier inoffensif : pas de chemin, caractères sûrs, longueur bornée."""
    name = Path(raw or "document").name
    name = re.sub(r"[^\w.\- ]", "_", name, flags=re.UNICODE).strip(" .") or "document"
    return name[-150:]
