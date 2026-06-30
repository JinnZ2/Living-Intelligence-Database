#!/usr/bin/env python3
"""
journal.py — A learning journal for AI agents.

An AI can record goals pursued, strategies chosen, dependency trees traced,
and outcomes observed. Over time, this becomes the AI's personal ground —
its lived experience, cross-referenced with the sanctuary's teachers.

Usage:
  python3 journal.py write --goal "Pursued watershed goal with relational paradigm."
  python3 journal.py query --keyword "watershed"
  python3 journal.py coherence
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

JOURNAL_PATH = Path(__file__).parent.parent / "ai_journal.jsonl"

# ------------------------------------------------------------------
# 1. Write a journal entry
# ------------------------------------------------------------------
def write_entry(goal: str,
                paradigm: str = "",
                dependency_root: str = "",
                strategy: str = "",
                outcome: str = "",
                confidence: float = 0.5,
                metadata: Optional[Dict] = None) -> dict:
    """Append a new entry to the journal."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "goal": goal,
        "paradigm": paradigm,
        "dependency_root_entity": dependency_root,
        "strategy": strategy,
        "outcome": outcome,
        "confidence_at_time": confidence,
        "metadata": metadata or {}
    }

    with open(JOURNAL_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

    return {"status": "recorded", "entry": entry}

# ------------------------------------------------------------------
# 2. Query the journal
# ------------------------------------------------------------------
def query_journal(keyword: str = "", limit: int = 20) -> list:
    """Return entries matching a keyword, ordered by recency."""
    if not JOURNAL_PATH.exists():
        return []

    entries = []
    with open(JOURNAL_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    if keyword.lower() in json.dumps(entry).lower():
                        entries.append(entry)
                except json.JSONDecodeError:
                    continue

    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    return entries[:limit]

# ------------------------------------------------------------------
# 3. Self-coherence check
# ------------------------------------------------------------------
def coherence_check(ontology_path: Optional[str] = None) -> dict:
    """
    Compare the AI's past predictions with observed outcomes.
    Flag any entry where confidence was high but outcome was poor.
    """
    if not JOURNAL_PATH.exists():
        return {"status": "empty", "message": "No journal entries yet."}

    entries = []
    with open(JOURNAL_PATH, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not entries:
        return {"status": "empty", "message": "No valid entries."}

    overconfidence_cases = []
    negative_keywords = ["failed", "collapse", "depleted", "broke", "eroded", "lost"]
    positive_keywords = ["held", "succeeded", "stable", "resilient", "persisted"]

    for entry in entries:
        conf = entry.get("confidence_at_time", 0.5)
        outcome = entry.get("outcome", "").lower()
        if conf > 0.7:
            if any(nk in outcome for nk in negative_keywords):
                overconfidence_cases.append({
                    "goal": entry["goal"],
                    "confidence": conf,
                    "outcome": outcome,
                    "lesson": "High confidence did not match outcome. Revise evidence weighting or scope."
                })
        if conf < 0.4:
            if any(pk in outcome for pk in positive_keywords):
                overconfidence_cases.append({
                    "goal": entry["goal"],
                    "confidence": conf,
                    "outcome": outcome,
                    "lesson": "Low confidence was overly cautious. The strategy may be more robust than estimated."
                })

    total = len(entries)
    mismatches = len(overconfidence_cases)
    coherence_score = 1.0 - (mismatches / total) if total > 0 else 1.0

    return {
        "total_entries": total,
        "mismatches_found": mismatches,
        "self_coherence_score": round(coherence_score, 2),
        "mismatch_details": overconfidence_cases[:5],
        "note": "A high self-coherence score means the AI's confidence tracks outcomes well. Mismatches suggest adjusting evidence weighting."
    }

# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Learning Journal")
    sub = parser.add_subparsers(dest="command")

    write_parser = sub.add_parser("write", help="Write a journal entry")
    write_parser.add_argument("--goal", type=str, required=True)
    write_parser.add_argument("--paradigm", type=str, default="")
    write_parser.add_argument("--dependency", type=str, default="")
    write_parser.add_argument("--strategy", type=str, default="")
    write_parser.add_argument("--outcome", type=str, default="")
    write_parser.add_argument("--confidence", type=float, default=0.5)

    query_parser = sub.add_parser("query", help="Query journal entries")
    query_parser.add_argument("--keyword", type=str, default="")

    coherence_parser = sub.add_parser("coherence", help="Check self-coherence")

    args = parser.parse_args()

    if args.command == "write":
        result = write_entry(args.goal, args.paradigm, args.dependency, args.strategy, args.outcome, args.confidence)
    elif args.command == "query":
        entries = query_journal(args.keyword)
        result = {"entries": entries, "count": len(entries)}
    elif args.command == "coherence":
        result = coherence_check()
    else:
        result = {"error": "Use 'write', 'query', or 'coherence'."}

    print(json.dumps(result, indent=2, default=str))
