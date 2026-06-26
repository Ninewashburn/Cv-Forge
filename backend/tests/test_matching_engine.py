"""Tests for the matching engine."""

import json
from pathlib import Path

from app.matching_engine import match_profile_to_offer
from app.models import FactItem, JobOfferAnalysis


def test_match_profile_to_offer():
    """Test that the matching engine correctly matches required skills."""
    facts_data = json.loads(Path("data/master_profile.sample.json").read_text(encoding="utf-8"))
    facts = [
        FactItem(
            id=item["id"],
            type=item["type"],
            title=item["title"],
            content=item["content"],
            tags=item.get("tags", []),
            validated=item.get("validated", False),
            proof_ids=item.get("proof_ids", []),
        )
        for item in facts_data
    ]
    offer = JobOfferAnalysis(
        title="Développeur Full Stack Laravel / Angular",
        required_skills=["Laravel", "Angular", "SQL", "API REST"],
    )
    matches = match_profile_to_offer(facts, offer)

    assert sorted(matches["matched"]) == sorted(["laravel", "angular", "sql", "api rest"])
    assert matches["missing"] == []
