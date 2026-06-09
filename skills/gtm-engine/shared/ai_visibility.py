"""
AI-visibility wedge helper.

In dry-run (the default), this reads the ai_visibility_signal field that the
caller already loaded from the CSV — no network calls needed.

In live mode the helper fetches the company's domain via shared/fetch.py and
calls Claude to classify the gap. This mirrors the entity_auditor logic without
importing the auditor's CLI entry point directly.

Usage
-----
from shared.ai_visibility import check_visibility

result = check_visibility(account, dry_run=True)
# result: {"has_gap": bool, "gap_summary": str, "strength": int 0-10}
"""

from __future__ import annotations

from shared.llm import query_json


def check_visibility(account: dict, dry_run: bool = True) -> dict:
    """
    Assess the AI-search visibility gap for a target account.

    Parameters
    ----------
    account  : dict with keys including domain, company, ai_visibility_signal
    dry_run  : if True, classifies the signal already in the account dict
               with no network call; if False, fetches the domain and runs
               a live gap check.

    Returns
    -------
    {
      "has_gap"     : bool,
      "gap_summary" : str (one plain sentence),
      "strength"    : int 1-10 (10 = clearest, most actionable gap),
    }
    """
    if dry_run:
        return _classify_from_signal(account)
    else:
        return _classify_live(account)


def _classify_from_signal(account: dict) -> dict:
    """Classify the pre-loaded ai_visibility_signal string."""
    signal = (account.get("ai_visibility_signal") or "").strip()
    if not signal:
        return {"has_gap": False, "gap_summary": "", "strength": 0}

    company = account.get("company", "")
    prompt = (
        "You are a B2B go-to-market analyst reviewing an AI search visibility signal.\n\n"
        f"Company: {company}\n"
        f"Signal: {signal}\n\n"
        "Return a JSON object with:\n"
        "  has_gap: true if there is a meaningful AI search visibility gap\n"
        "  gap_summary: one plain sentence describing the gap (max 20 words), or empty string if none\n"
        "  strength: integer 1-10 (10 = clearest, most actionable gap with a named competitor)\n\n"
        "Score 8-10 only when a specific competitor is named, or the company is completely absent from "
        "core category queries. Score 5-7 for partial absence. Score 1-4 for vague or unclear gaps."
    )
    result = query_json(prompt)
    if isinstance(result, dict) and "has_gap" in result:
        return {
            "has_gap": bool(result.get("has_gap", False)),
            "gap_summary": str(result.get("gap_summary", "")),
            "strength": int(result.get("strength", 0)),
        }
    return {"has_gap": bool(signal), "gap_summary": signal[:120], "strength": 5}


def _classify_live(account: dict) -> dict:
    """
    Live gap check: fetch the domain and run a Claude classification.

    TODO: Wire to entity_auditor logic for a full audit.
    For now, fetches the homepage and asks Claude about AI visibility.
    Requires an internet connection.
    """
    domain = account.get("domain", "").strip()
    company = account.get("company", "")
    industry = account.get("industry", "")

    if not domain:
        print(f"  [ai_visibility] No domain for {company}. Skipping live check.")
        return {"has_gap": False, "gap_summary": "", "strength": 0}

    try:
        from shared.fetch import fetch
        url = domain if domain.startswith("http") else f"https://{domain}"
        page = fetch(url)
        snippet = (page.body or "")[:800]
    except Exception as exc:
        print(f"  [ai_visibility] Fetch failed for {domain}: {exc}")
        snippet = ""

    prompt = (
        "You are assessing whether a company likely has an AI search visibility gap.\n\n"
        f"Company: {company}\n"
        f"Industry: {industry}\n"
        f"Homepage snippet: {snippet}\n\n"
        "Based on typical B2B SaaS patterns, estimate whether this company is likely absent from "
        "AI engine answers for its core category queries.\n\n"
        "Return JSON with: has_gap (bool), gap_summary (one sentence max 20 words), strength (int 1-10).\n"
        "Be conservative — mark has_gap true only when there is clear evidence of a category."
    )
    result = query_json(prompt)
    if isinstance(result, dict) and "has_gap" in result:
        return {
            "has_gap": bool(result.get("has_gap", False)),
            "gap_summary": str(result.get("gap_summary", "")),
            "strength": int(result.get("strength", 0)),
        }
    return {"has_gap": False, "gap_summary": "", "strength": 0}
