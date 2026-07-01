"""Schémas I/O du micro-tracking de candidatures."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ApplicationStatus, ReadBase


class ApplicationCreate(BaseModel):
    offer_id: str
    variant_id: str | None = None
    notes: str = ""


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    notes: str | None = None


class ApplicationRead(ReadBase):
    offer_id: str
    variant_id: str | None = None
    status: ApplicationStatus
    sent_at: datetime
    notes: str
