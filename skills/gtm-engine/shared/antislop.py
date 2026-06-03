"""
Anti-slop gate for all human-facing prose.

Usage:
    from shared.antislop import clean

    polished = clean(draft_text)                  # uses built-in rules
    polished = clean(draft_text, rules_path="antislop_rules.md")  # file overrides

The gate is a hard gate, not a flag. Failed text is rewritten, not just marked.
Two passes:
  1. Rule check: scan for banned words, banned phrases, em dashes, hollow intensifiers.
  2. Claude rewrite: strip AI tells and enforce style rules regardless of pass/fail.
"""

import re
from pathlib import Path

from shared.llm import query_text

# ── Built-in rules (from antislop_rules.md) ───────────────────────────────────

_BANNED_WORDS = {
    "delve", "moreover", "furthermore", "albeit", "indeed", "utilize", "leverage",
    "facilitate", "robust", "seamless", "comprehensive", "cutting-edge", "holistic",
    "synergy", "paradigm", "innovative", "transformative", "empower", "realm",
    "tapestry", "multifaceted", "nuanced", "underscore", "testament", "myriad",
    "plethora", "illuminate", "foster", "cultivate", "spearhead", "bolster",
    "pivotal", "embark", "stakeholder", "bandwidth", "actionable", "ecosystem",
    "streamline", "elevate", "harness", "unlock", "tailor", "compelling",
    "powerful", "impactful", "crucial", "significant", "ensure", "optimal",
}

_BANNED_PHRASES = [
    "it's important to note", "it's worth mentioning", "it goes without saying",
    "in today's", "let's dive into", "without further ado", "in this article",
    "as we all know", "let's break it down", "let's unpack", "to be fair",
    "to be honest", "at the end of the day", "when it comes to", "in terms of",
    "it's crucial to", "it's no secret", "it's clear that", "needless to say",
    "and honestly", "i'll be honest", "if i'm being honest", "candidly",
    "frankly,", "real talk", "the truth is", "i won't sugarcoat",
    "exciting opportunity", "best practice", "value-add", "double down",
    "deep dive", "circle back", "shed light on", "pave the way", "set the stage",
    "raise the bar", "move the needle",
]

_HOLLOW_INTENSIFIERS = re.compile(
    r"\b(very|really|quite|rather|somewhat)\b", re.IGNORECASE
)

_EM_DASH = re.compile(r"[—–]|--")  # em dash, en dash, double hyphen

_BUILT_IN_RULES_SUMMARY = """
Hard rules for all prose:
- No em dashes. Use commas, periods, colons, or semicolons instead.
- Short declarative sentences. Subject and verb first.
- Active voice.
- No filler openers: do not start with "It's important to note", "In today's...", etc.
- No summary closers that recap what was just said.
- No hollow intensifiers: very, really, quite, rather, somewhat.
- Cut banned words: delve, leverage, robust, seamless, synergy, transformative,
  empower, pivotal, embark, stakeholder, actionable, ecosystem, compelling,
  impactful, ensure, optimal, and similar corporate filler.
- State claims directly. No empty hedges.
- Evidence first, then interpretation.
"""


# ── Public API ────────────────────────────────────────────────────────────────

def clean(text: str, rules_path: str | Path | None = None) -> str:
    """
    Run the anti-slop gate on text. Returns cleaned prose.
    Always rewrites via Claude regardless of whether rule violations were found.
    """
    rules_summary = _load_rules(rules_path) if rules_path else _BUILT_IN_RULES_SUMMARY
    violations = _find_violations(text)

    prompt = _build_rewrite_prompt(text, rules_summary, violations)
    cleaned = query_text(prompt)

    return cleaned.strip()


def check(text: str, rules_path: str | Path | None = None) -> list[str]:
    """
    Return a list of violation descriptions without rewriting.
    Useful for diagnostics or building before/after comparisons.
    """
    return _find_violations(text)


# ── Internal ──────────────────────────────────────────────────────────────────

def _load_rules(rules_path: str | Path) -> str:
    path = Path(rules_path)
    if not path.exists():
        print(f"[antislop] Rules file not found: {path}. Using built-in rules.")
        return _BUILT_IN_RULES_SUMMARY
    return path.read_text(encoding="utf-8")


def _find_violations(text: str) -> list[str]:
    found = []

    if _EM_DASH.search(text):
        found.append("Contains em dash or en dash.")

    lower = text.lower()
    for word in _BANNED_WORDS:
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        if pattern.search(text):
            found.append(f"Banned word: '{word}'")

    for phrase in _BANNED_PHRASES:
        if phrase.lower() in lower:
            found.append(f"Banned phrase: '{phrase}'")

    for match in _HOLLOW_INTENSIFIERS.finditer(text):
        found.append(f"Hollow intensifier: '{match.group()}'")

    return found


def _build_rewrite_prompt(text: str, rules: str, violations: list[str]) -> str:
    violation_block = ""
    if violations:
        violation_block = (
            "\n\nSpecific violations found that must be fixed:\n"
            + "\n".join(f"- {v}" for v in violations)
        )

    return f"""Rewrite the following text to remove AI-style writing and enforce these style rules:

{rules}{violation_block}

Return only the rewritten text. Do not explain what you changed. Do not add a preamble or closing remark.

TEXT TO REWRITE:
{text}"""
