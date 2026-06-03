"""
Query an AI engine with a prompt and return its raw text answer.

Claude is the active default, routed through shared/llm.py.
OpenAI, Perplexity, and Gemini are stubbed: they require their own API
keys and are skipped gracefully if those keys are absent.

Usage:
    from shared.adapters.engines import query_engines

    results = query_engines("What is contract testing?", engines=["claude"])
    # Returns: {"claude": "Contract testing is...", "openai": None, ...}

    # With all engines (paid keys loaded from env):
    results = query_engines("...", engines=["claude", "openai", "perplexity", "gemini"])
"""

import os

from shared.llm import query_text


def query_engines(
    prompt: str,
    engines: list[str] | None = None,
) -> dict[str, str | None]:
    """
    Query one or more AI engines. Returns a dict of engine name → answer (or None if skipped).

    Args:
        prompt:  The question or instruction to send.
        engines: Which engines to query. Defaults to ["claude"] (the free default).
                 Options: "claude", "openai", "perplexity", "gemini".
    """
    if engines is None:
        engines = ["claude"]

    results: dict[str, str | None] = {}

    for engine in engines:
        name = engine.lower().strip()
        if name == "claude":
            results["claude"] = _query_claude(prompt)
        elif name == "openai":
            results["openai"] = _query_openai(prompt)
        elif name == "perplexity":
            results["perplexity"] = _query_perplexity(prompt)
        elif name == "gemini":
            results["gemini"] = _query_gemini(prompt)
        else:
            print(f"[engines] Unknown engine '{engine}' — skipped.")
            results[engine] = None

    return results


# ── Active adapter: Claude ────────────────────────────────────────────────────

def _query_claude(prompt: str) -> str:
    """Route through shared/llm.py — subscription auth, no API key."""
    return query_text(prompt)


# ── Stubbed adapters ──────────────────────────────────────────────────────────
# TODO: implement each adapter by installing the vendor SDK and reading its key.
# Each returns None and prints a notice when the key is absent, rather than
# raising — the caller skips the result and reports the gap in output.

def _query_openai(prompt: str) -> str | None:
    # TODO: `pip install openai` and set OPENAI_API_KEY to activate.
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        print("[engines] OpenAI skipped: OPENAI_API_KEY not set.")
        return None
    try:
        import openai  # type: ignore[import]
        client = openai.OpenAI(api_key=key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        print(f"[engines] OpenAI error: {exc}")
        return None


def _query_perplexity(prompt: str) -> str | None:
    # TODO: set PERPLEXITY_API_KEY to activate.
    # Perplexity uses an OpenAI-compatible API at https://api.perplexity.ai.
    key = os.environ.get("PERPLEXITY_API_KEY")
    if not key:
        print("[engines] Perplexity skipped: PERPLEXITY_API_KEY not set.")
        return None
    try:
        import openai  # type: ignore[import]
        client = openai.OpenAI(api_key=key, base_url="https://api.perplexity.ai")
        response = client.chat.completions.create(
            model="llama-3.1-sonar-large-128k-online",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        print(f"[engines] Perplexity error: {exc}")
        return None


def _query_gemini(prompt: str) -> str | None:
    # TODO: `pip install google-generativeai` and set GEMINI_API_KEY to activate.
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("[engines] Gemini skipped: GEMINI_API_KEY not set.")
        return None
    try:
        import google.generativeai as genai  # type: ignore[import]
        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text or ""
    except Exception as exc:
        print(f"[engines] Gemini error: {exc}")
        return None
