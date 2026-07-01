"""Schémas I/O du profil maître."""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ReadBase


class MasterProfileBase(BaseModel):
    full_name: str = ""
    headline: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    links: list[str] = Field(default_factory=list)
    summary: str = ""


class MasterProfileCreate(MasterProfileBase):
    raw_import_text: str | None = None


class MasterProfileUpdate(BaseModel):
    full_name: str | None = None
    headline: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    links: list[str] | None = None
    summary: str | None = None
    raw_import_text: str | None = None


class MasterProfileRead(MasterProfileBase, ReadBase):
    raw_import_text: str | None = None
