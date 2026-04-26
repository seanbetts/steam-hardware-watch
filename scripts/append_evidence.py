#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Append one evidence record to the skill JSONL ledger.")
    parser.add_argument("--file", required=True, help="Path to evidence.jsonl")
    parser.add_argument("--date-checked", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--entity", required=True)
    parser.add_argument("--claim", required=True)
    parser.add_argument("--evidence-type", required=True)
    parser.add_argument("--confidence", required=True, choices=["high", "medium", "low"])
    parser.add_argument("--ref", required=True, help="URL or local path")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    record = {
        "date_checked": args.date_checked,
        "source": args.source,
        "entity": args.entity,
        "claim": args.claim,
        "evidence_type": args.evidence_type,
        "confidence": args.confidence,
        "ref": args.ref,
        "notes": args.notes,
    }

    target = Path(args.file)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=True) + "\n")


if __name__ == "__main__":
    main()
