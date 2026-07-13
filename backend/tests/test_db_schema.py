"""Tests du schéma sync-ready : UUID v4, timestamps, soft delete, contraintes."""

import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core import db as core_db
from app.db import Base, Fact, MasterProfile, Proof, ProofFact


@pytest.fixture
def session(tmp_path, monkeypatch):
    monkeypatch.setenv("CVFORGE_DATA", str(tmp_path))
    core_db.reset_engine()
    engine = core_db.get_engine()
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        yield s
    core_db.reset_engine()


def _make_profile(session: Session) -> MasterProfile:
    profile = MasterProfile(full_name="Ada Lovelace")
    session.add(profile)
    session.commit()
    return profile


def test_primary_key_is_uuid4(session):
    profile = _make_profile(session)
    parsed = uuid.UUID(profile.id)
    assert parsed.version == 4


def test_timestamps_are_set(session):
    profile = _make_profile(session)
    assert profile.created_at is not None
    assert profile.updated_at is not None
    assert profile.deleted_at is None


def test_updated_at_moves_on_update(session):
    profile = _make_profile(session)
    before = profile.updated_at
    profile.headline = "Développeuse"
    session.commit()
    assert profile.updated_at >= before


def test_soft_delete_sets_deleted_at(session):
    profile = _make_profile(session)
    profile.soft_delete()
    session.commit()
    assert profile.is_deleted
    assert profile.deleted_at is not None
    # La ligne existe toujours physiquement - jamais de DELETE.
    assert session.get(MasterProfile, profile.id) is not None


def test_proof_fact_link_is_unique(session):
    profile = _make_profile(session)
    fact = Fact(profile_id=profile.id, type="skill", title="Angular")
    proof = Proof(type="link", title="Dépôt GitHub")
    session.add_all([fact, proof])
    session.commit()

    session.add(ProofFact(proof_id=proof.id, fact_id=fact.id))
    session.commit()

    session.add(ProofFact(proof_id=proof.id, fact_id=fact.id))
    with pytest.raises(IntegrityError):
        session.commit()


def test_foreign_keys_are_enforced(session):
    session.add(Fact(profile_id="00000000-0000-4000-8000-000000000000",
                     type="skill", title="Orphelin"))
    with pytest.raises(IntegrityError):
        session.commit()
