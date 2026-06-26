"""Data model definitions for CVForge.

This module defines dataclasses representing the core entities of the
application. These classes are used to load and manipulate structured
information about a candidate's professional background, proofs of experience
and the output of job offer parsing and CV generation.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FactItem:
    """Represents a validated fact about the user's professional experience."""

    id: str
    type: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    validated: bool = False
    proof_ids: List[str] = field(default_factory=list)


@dataclass
class ProofItem:
    """Represents supporting evidence for a FactItem."""

    id: str
    type: str
    title: str
    content: str
    confidentiality: str = "private"
    linked_fact_ids: List[str] = field(default_factory=list)


@dataclass
class JobOfferAnalysis:
    """Holds the structured representation of a job offer after parsing."""

    title: str
    company: Optional[str] = None
    required_skills: List[str] = field(default_factory=list)
    optional_skills: List[str] = field(default_factory=list)
    responsibilities: List[str] = field(default_factory=list)
    weak_signals: List[str] = field(default_factory=list)


@dataclass
class GeneratedSentence:
    """Represents a generated sentence or bullet point for the tailored CV."""

    text: str
    source_fact_ids: List[str] = field(default_factory=list)
    source_proof_ids: List[str] = field(default_factory=list)
    status: str = "valid"
    reason: Optional[str] = None


@dataclass
class JobBookmark:
    """Represents a minimal personal bookmark for a job offer."""

    url: str
    title: str
    company: str
    source: str
    captured_at: str
    status: str = "bookmarked"


@dataclass
class WatchItem:
    """Represents a minimal local-first resource tracked by CVForge."""

    url: str
    title: str
    source: str
    item_type: str
    captured_at: str
    status: str = "bookmarked"
    company: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    related_skill: Optional[str] = None
