"""Tables CVForge V1 — cœur du parcours : profil → preuves → offre → variante.

Principe de traçabilité (anti-hallucination) : chaque
:class:`GeneratedSentence` référence les faits (``source_fact_ids``) et
preuves (``source_proof_ids``) qui la justifient ; une phrase sans source
est rejetée par le moteur de validation, jamais exportée.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, SyncReadyMixin


class MasterProfile(Base, SyncReadyMixin):
    """Source de vérité : l'utilisateur, champs essentiels uniquement (V1)."""

    __tablename__ = "master_profile"

    full_name: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    headline: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    email: Mapped[str] = mapped_column(String(320), nullable=False, default="")
    phone: Mapped[str] = mapped_column(String(50), nullable=False, default="")
    location: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    links: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # Texte brut du CV importé (PDF/collage) — conservé pour re-parsing et Avant/Après.
    raw_import_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    facts: Mapped[list["Fact"]] = relationship(back_populates="profile")


class Fact(Base, SyncReadyMixin):
    """Fait validé du parcours (expérience, compétence, projet, formation…)."""

    __tablename__ = "fact"

    profile_id: Mapped[str] = mapped_column(
        ForeignKey("master_profile.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    validated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    profile: Mapped[MasterProfile] = relationship(back_populates="facts")
    proof_links: Mapped[list["ProofFact"]] = relationship(back_populates="fact")

    @property
    def proof_ids(self) -> list[str]:
        return [link.proof_id for link in self.proof_links if link.deleted_at is None]


class Proof(Base, SyncReadyMixin):
    """Preuve de la banque : texte, lien ou document, avec niveau de confidentialité."""

    __tablename__ = "proof"

    type: Mapped[str] = mapped_column(String(30), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    confidentiality: Mapped[str] = mapped_column(
        String(20), nullable=False, default="private"
    )
    # Nom de fichier relatif au dossier de données (preuves de type document).
    file_name: Mapped[str | None] = mapped_column(String(300), nullable=True)

    fact_links: Mapped[list["ProofFact"]] = relationship(back_populates="proof")

    @property
    def fact_ids(self) -> list[str]:
        return [link.fact_id for link in self.fact_links if link.deleted_at is None]


class ProofFact(Base, SyncReadyMixin):
    """Liaison N–N fait ↔ preuve (table à part entière : sync-ready + soft delete)."""

    __tablename__ = "proof_fact"
    __table_args__ = (UniqueConstraint("proof_id", "fact_id", name="uq_proof_fact"),)

    proof_id: Mapped[str] = mapped_column(ForeignKey("proof.id"), nullable=False, index=True)
    fact_id: Mapped[str] = mapped_column(ForeignKey("fact.id"), nullable=False, index=True)

    proof: Mapped[Proof] = relationship(back_populates="fact_links")
    fact: Mapped[Fact] = relationship(back_populates="proof_links")


class Offer(Base, SyncReadyMixin):
    """Offre d'emploi importée (texte collé) et son analyse structurée."""

    __tablename__ = "offer"

    title: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    company: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Référence saisie par l'utilisateur — jamais fetchée (aucun appel réseau).
    source_url: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    # Analyse : mots-clés pondérés [[mot, fréquence], …] et extractions.
    keywords: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    required_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    optional_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    responsibilities: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    variants: Mapped[list["CvVariant"]] = relationship(back_populates="offer")


class CvVariant(Base, SyncReadyMixin):
    """Variante de CV adaptée à une offre — ce que l'Avant/Après compare et valide."""

    __tablename__ = "cv_variant"

    profile_id: Mapped[str] = mapped_column(
        ForeignKey("master_profile.id"), nullable=False, index=True
    )
    offer_id: Mapped[str] = mapped_column(ForeignKey("offer.id"), nullable=False, index=True)
    recommended_title: Mapped[str] = mapped_column(String(300), nullable=False, default="")
    recommended_summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    # Texte "après" validé dans l'Avant/Après (adaptation manuelle ou copilote).
    adapted_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    match_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")

    offer: Mapped[Offer] = relationship(back_populates="variants")
    profile: Mapped[MasterProfile] = relationship()
    sentences: Mapped[list["GeneratedSentence"]] = relationship(
        back_populates="variant", order_by="GeneratedSentence.position"
    )


class GeneratedSentence(Base, SyncReadyMixin):
    """Phrase générée, tracée jusqu'aux faits et preuves qui la justifient."""

    __tablename__ = "generated_sentence"

    variant_id: Mapped[str] = mapped_column(
        ForeignKey("cv_variant.id"), nullable=False, index=True
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source_fact_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    source_proof_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="valid")
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    variant: Mapped[CvVariant] = relationship(back_populates="sentences")


class Application(Base, SyncReadyMixin):
    """Micro-tracking : une candidature exportée, son statut en 3 clics max."""

    __tablename__ = "application"

    offer_id: Mapped[str] = mapped_column(ForeignKey("offer.id"), nullable=False, index=True)
    variant_id: Mapped[str | None] = mapped_column(
        ForeignKey("cv_variant.id"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="envoyee")
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")

    offer: Mapped[Offer] = relationship()
    variant: Mapped[CvVariant | None] = relationship()
