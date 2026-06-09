"""
Shared ICP fit scoring.

Refactored from pipeline_engine so both pipeline_engine and prospecting_engine
use the same implementation. Call score_fit_batch() with a list of record dicts
and the ICP text; receive the same list back with fit fields attached.

pipeline_engine imports this for contacts.
prospecting_engine imports this for target accounts.
"""

from __future__ import annotations

import json

from shared.llm import query_json


def score_fit_batch(records: list[dict], icp_text: str, name_key: str = "name") -> list[dict]:
    """
    Batch ICP fit scoring via a single Claude call.

    Each record is a dict. The caller should include whatever identifying fields
    are relevant (name/title/company/industry/company_size/etc.).

    Attaches to each record:
        fit_score       int 1-10
        fit_reason      str, one plain sentence
        disqualified    bool
        disqualify_reason str

    Returns the same list (mutated in place and returned).
    """
    # Build minimal summaries for the Claude call — drop internal/private keys
    _skip = {"_page_snippet", "_raw", "outreach_message", "warmth_tier", "warmth_score"}
    summaries = []
    for i, rec in enumerate(records):
        summary = {"index": i}
        for k, v in rec.items():
            if k not in _skip and not k.startswith("_"):
                summary[k] = v
        summaries.append(summary)

    prompt = (
        "You are a B2B sales qualifier. Score each record against the ICP below.\n\n"
        f"ICP:\n{icp_text}\n\n"
        f"Records:\n{json.dumps(summaries, indent=2)}\n\n"
        "Return a JSON array — one object per record in the same order — with:\n"
        "  index: same integer as input\n"
        "  fit_score: integer 1-10 (10 = perfect ICP match)\n"
        "  fit_reason: one plain sentence, max 15 words, no corporate filler\n"
        "  disqualified: true if this record clearly matches an ICP disqualifier\n"
        "  disqualify_reason: short phrase if disqualified, else empty string\n\n"
        "Be direct. Score only on what is stated in the ICP. Do not fabricate details."
    )

    results = query_json(prompt)

    if not isinstance(results, list):
        print("  [scoring] Unexpected fit-scoring response. Defaulting scores to 5.")
        results = [
            {"index": i, "fit_score": 5, "fit_reason": "Unable to score.", "disqualified": False, "disqualify_reason": ""}
            for i in range(len(records))
        ]

    score_map = {r["index"]: r for r in results if isinstance(r, dict) and "index" in r}

    for i, rec in enumerate(records):
        sc = score_map.get(i, {})
        rec["fit_score"] = int(sc.get("fit_score", 5))
        rec["fit_reason"] = sc.get("fit_reason", "")
        rec["disqualified"] = bool(sc.get("disqualified", False))
        rec["disqualify_reason"] = sc.get("disqualify_reason", "")

    return records
