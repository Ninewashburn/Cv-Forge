"""Validation engine for CVForge.

This module performs checks on the generated CV variant to ensure it adheres to
the anti-hallucination rules. It verifies that every generated sentence
references at least one fact identifier and lists warnings for any job offer
requirements that are not covered by the candidate's facts.
"""

from typing import Dict, List


def validate_cv_variant(
    variant: Dict[str, object], missing_requirements: List[str]
) -> Dict[str, object]:
    """Validate a generated CV variant by enforcing anti-hallucination rules."""
    warnings: List[str] = []
    for sentence in variant.get("generated_sentences", []):
        if not sentence.get("source_fact_ids"):
            warnings.append(
                f"La phrase '{sentence.get('text')}' n'a aucune source et a été rejetée."
            )
            sentence["status"] = "rejected"
            sentence["reason"] = "Sans source"

    for keyword in missing_requirements:
        warnings.append(
            f"Compétence demandée '{keyword}' absente de la base de faits validés."
        )

    variant["validation_warnings"] = warnings
    return variant
