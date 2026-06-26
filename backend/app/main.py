"""Main CLI entry point for CVForge's backend engine.

This script demonstrates the CVForge flow: it loads a profile and proofs from
JSON files, reads a job offer from a text file, parses and matches the offer,
generates a CV variant, validates it, and writes the result to a JSON file. It
serves as a minimal example of the Extract → Transform → Validate → Load
process described in the project vision.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List

from .generation_engine import generate_cv_variant
from .matching_engine import match_profile_to_offer
from .models import FactItem
from .offer_parser import parse_job_offer
from .validation_engine import validate_cv_variant


def load_facts(path: Path) -> List[FactItem]:
    """Load fact items from a JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    facts: List[FactItem] = []
    for item in data:
        facts.append(
            FactItem(
                id=item["id"],
                type=item["type"],
                title=item["title"],
                content=item["content"],
                tags=item.get("tags", []),
                validated=item.get("validated", False),
                proof_ids=item.get("proof_ids", []),
            )
        )
    return facts


def main() -> None:
    parser = argparse.ArgumentParser(description="CVForge engine CLI")
    parser.add_argument(
        "--profile",
        required=True,
        type=Path,
        help="Path to the JSON file containing fact items.",
    )
    parser.add_argument(
        "--proofs",
        required=False,
        type=Path,
        help="Path to the JSON file containing proof items.",
    )
    parser.add_argument(
        "--offer",
        required=True,
        type=Path,
        help="Path to the text file containing the job offer.",
    )
    parser.add_argument(
        "--out", required=True, type=Path, help="Path to the output JSON file."
    )
    args = parser.parse_args()

    facts = load_facts(args.profile)
    if args.proofs and args.proofs.exists():
        _ = json.loads(args.proofs.read_text(encoding="utf-8"))

    offer_text = args.offer.read_text(encoding="utf-8")
    offer_analysis = parse_job_offer(offer_text)
    matches = match_profile_to_offer(facts, offer_analysis)
    variant = generate_cv_variant(facts, offer_analysis, matches)
    validated_variant = validate_cv_variant(variant, matches.get("missing", []))

    output_data: Dict[str, object] = {
        "offer_analysis": offer_analysis.__dict__,
        "matches": matches,
        "cv_variant": validated_variant,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Résultat écrit dans {args.out}")


if __name__ == "__main__":
    main()
