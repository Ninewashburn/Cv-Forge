"""Socle des modèles : règles de schéma NON NÉGOCIABLES (CLAUDE.md).

Toutes les tables héritent de :class:`SyncReadyMixin` :

- clé primaire **UUID v4** (jamais d'auto-increment) ;
- ``created_at`` / ``updated_at`` en UTC ;
- **soft delete** via ``deleted_at`` (jamais de DELETE physique).

Ce schéma anticipe la sync cloud (V3) : les UUIDs évitent les collisions
entre appareils, les timestamps permettent la réconciliation, le soft
delete permet de propager les suppressions.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class SyncReadyMixin:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_utcnow, onupdate=_utcnow
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    def soft_delete(self) -> None:
        self.deleted_at = _utcnow()

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
