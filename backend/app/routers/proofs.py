"""CRUD de la banque de preuves + pièce jointe (stockée dans le dossier de données)."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.schemas import ProofCreate, ProofRead, ProofUpdate
from app.services import proof_service

router = APIRouter(prefix="/api/proofs", tags=["proofs"])


@router.get("", response_model=list[ProofRead])
def list_proofs(session: Session = Depends(get_session)) -> list[ProofRead]:
    return [ProofRead.model_validate(p) for p in proof_service.list_proofs(session)]


@router.post("", response_model=ProofRead, status_code=201)
def create_proof(data: ProofCreate, session: Session = Depends(get_session)) -> ProofRead:
    return ProofRead.model_validate(proof_service.create_proof(session, data))


@router.get("/{proof_id}", response_model=ProofRead)
def get_proof(proof_id: str, session: Session = Depends(get_session)) -> ProofRead:
    return ProofRead.model_validate(proof_service.get_proof(session, proof_id))


@router.patch("/{proof_id}", response_model=ProofRead)
def update_proof(
    proof_id: str, data: ProofUpdate, session: Session = Depends(get_session)
) -> ProofRead:
    return ProofRead.model_validate(proof_service.update_proof(session, proof_id, data))


@router.delete("/{proof_id}", status_code=204)
def delete_proof(proof_id: str, session: Session = Depends(get_session)) -> None:
    proof_service.soft_delete_proof(session, proof_id)


@router.put("/{proof_id}/file", response_model=ProofRead)
async def attach_file(
    proof_id: str, file: UploadFile, session: Session = Depends(get_session)
) -> ProofRead:
    """Attache la pièce jointe (une par preuve — remplace l'existante). 100 % local."""
    content = await file.read()
    try:
        proof = proof_service.attach_file(
            session, proof_id, file.filename or "document", content
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ProofRead.model_validate(proof)


@router.get("/{proof_id}/file")
def download_file(proof_id: str, session: Session = Depends(get_session)) -> FileResponse:
    """Renvoie la pièce jointe telle quelle (téléchargement/aperçu navigateur)."""
    path, display_name = proof_service.attached_file(session, proof_id)
    return FileResponse(path, filename=display_name)
