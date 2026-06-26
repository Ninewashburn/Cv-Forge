"""Parsing logic for job offers.

This module contains functions to extract basic information from raw job
offers. The initial implementation uses simple keyword matching and rudimentary
heuristics; future versions should incorporate more sophisticated natural
language processing tailored to job offer texts.
"""

import re
from typing import List

from .models import JobOfferAnalysis


def parse_job_offer(text: str) -> JobOfferAnalysis:
    """Parse a raw job offer text into structured data."""
    lower_text = text.lower()
    possible_skills = [
        "angular",
        "laravel",
        "spring",
        "python",
        "java",
        "sql",
        "docker",
        "api",
        "rest",
        "aws",
        "cloud",
    ]
    required = [kw for kw in possible_skills if kw in lower_text]
    optional: List[str] = []
    sentences = re.split(r"[.!?\n]+", text)
    action_verbs = [
        "développer",
        "develop",
        "concevoir",
        "design",
        "maintenir",
        "maintain",
        "optimiser",
        "analyser",
        "analyze",
    ]
    responsibilities = [
        sentence.strip()
        for sentence in sentences
        if any(verb in sentence.lower() for verb in action_verbs)
    ]
    return JobOfferAnalysis(
        title="",
        company=None,
        required_skills=required,
        optional_skills=optional,
        responsibilities=responsibilities,
        weak_signals=[],
    )
