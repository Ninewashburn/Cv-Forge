"""Generation engine for CVForge.

This module creates a tailored CV variant based on matched facts and a job
offer analysis. Each sentence generated must reference fact identifiers,
ensuring that nothing is invented.
"""

from typing import Dict, List

from .models import FactItem, GeneratedSentence, JobOfferAnalysis


def generate_cv_variant(
    facts: List[FactItem], offer: JobOfferAnalysis, matches: Dict[str, List[str]]
) -> Dict[str, object]:
    """Build a simple CV variant structure based on matched facts and the job offer."""
    recommended_title = (
        f"Spécialiste {offer.required_skills[0].capitalize()}"
        if offer.required_skills
        else "Candidat"
    )
    matched_keywords = set(matches.get("matched", []))
    selected_facts = [
        fact for fact in facts if any(tag.lower() in matched_keywords for tag in fact.tags)
    ]
    summary_parts = [fact.title for fact in selected_facts]
    recommended_summary = " | ".join(summary_parts) if summary_parts else ""

    sentences: List[GeneratedSentence] = []
    for fact in selected_facts:
        sentences.append(
            GeneratedSentence(
                text=fact.content,
                source_fact_ids=[fact.id],
                source_proof_ids=fact.proof_ids,
                status="valid",
            )
        )

    return {
        "recommended_title": recommended_title,
        "recommended_summary": recommended_summary,
        "selected_fact_ids": [fact.id for fact in selected_facts],
        "generated_sentences": [sentence.__dict__ for sentence in sentences],
    }
