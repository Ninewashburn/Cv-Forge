"""Backup ZIP : export/import complet des données - « tes données t'appartiennent »."""

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import Response

from app.services import backup_service

router = APIRouter(prefix="/api/backup", tags=["backup"])


@router.get("/export")
def export_backup() -> Response:
    """Archive ZIP du dossier de données (base + fichiers de preuves)."""
    content, filename = backup_service.export_backup()
    return Response(
        content=content,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/import", status_code=204)
async def import_backup(file: UploadFile) -> None:
    """Restaure un backup : remplace TOUTES les données par celles de l'archive."""
    content = await file.read()
    try:
        backup_service.import_backup(content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
