"""Variantes de CV : lecture, adaptation (texte « après »), export PDF, suppression."""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.db import get_session
from app.schemas import CvVariantRead, CvVariantUpdate
from app.services import pdf_service, variant_service

router = APIRouter(prefix="/api/variants", tags=["variants"])


@router.get("/{variant_id}", response_model=CvVariantRead)
def get_variant(variant_id: str, session: Session = Depends(get_session)) -> CvVariantRead:
    return CvVariantRead.model_validate(variant_service.get_variant(session, variant_id))


@router.patch("/{variant_id}", response_model=CvVariantRead)
def update_variant(
    variant_id: str, data: CvVariantUpdate, session: Session = Depends(get_session)
) -> CvVariantRead:
    return CvVariantRead.model_validate(
        variant_service.update_variant(session, variant_id, data)
    )


@router.delete("/{variant_id}", status_code=204)
def delete_variant(variant_id: str, session: Session = Depends(get_session)) -> None:
    variant_service.soft_delete_variant(session, variant_id)


@router.get("/{variant_id}/pdf")
def variant_pdf(variant_id: str, session: Session = Depends(get_session)) -> Response:
    """PDF propre et parsable du texte « après » validé (fpdf2, 100 % local)."""
    content, filename = pdf_service.variant_pdf(session, variant_id)
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
