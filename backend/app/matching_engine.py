"""Matching engine for CVForge.

This module compares a candidate's fact base with a parsed job offer and
produces a basic matching report. The report identifies which requirements are
met and which are missing. The matching is case-insensitive and relies on fact
tags to represent the candidate's skills and experiences.
"""

from typing import Dict, List

from .models import FactItem, JobOfferAnalysis


def match_profile_to_offer(
    facts: List[FactItem], offer: JobOfferAnalysis
) -> Dict[str, List[str]]:
    """Compare a list of FactItems against a job offer analysis."""
    fact_keywords = {tag.lower() for fact in facts for tag in fact.tags}
    required_keywords = [kw.lower() for kw in offer.required_skills]
    matched = [kw for kw in required_keywords if kw in fact_keywords]
    missing = [kw for kw in required_keywords if kw not in fact_keywords]
    return {"matched": matched, "missing": missing}
