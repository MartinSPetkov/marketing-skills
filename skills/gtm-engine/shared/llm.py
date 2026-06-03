"""
Single point of access for all Claude calls in this repo.

Authentication: Claude subscription via `claude -p` (headless CLI).
No API key. No anthropic SDK. If ANTHROPIC_API_KEY is set in the
environment, this module refuses to run — it would silently bill the
API account instead of the subscription.

Usage:
    from shared.llm import query_text, query_json

    text = query_text("Summarise this in one sentence: ...")
    data = query_json("Return JSON with keys name and score: ...", schema_hint="...")
"""

import json
import os
import subprocess
import time

# ── Model config ─────────────────────────────────────────────────────────────
MODEL = "claude-sonnet-4-6"

# Maximum retries on transient subprocess failure (not rate limits)
_MAX_RETRIES = 3
_RETRY_DELAY = 2.0  # seconds between retries

# Timeout for subprocess calls. The brief assembly and similar large-prompt
# tasks can take 3-4 minutes on Claude Sonnet via subscription auth.
_SUBPROCESS_TIMEOUT = 300  # seconds


# ── Startup guard ─────────────────────────────────────────────────────────────
def _check_no_api_key() -> None:
    if os.environ.get("ANTHROPIC_API_KEY"):
        raise EnvironmentError(
            "\n"
            "ANTHROPIC_API_KEY is set in your environment.\n"
            "This repo authenticates through your Claude subscription via `claude -p`.\n"
            "If ANTHROPIC_API_KEY is present, Claude Code bills your API account\n"
            "instead of your subscription — which is almost certainly not what you want.\n"
            "\n"
            "Fix: run `unset ANTHROPIC_API_KEY` in this shell, then try again.\n"
            "Confirm your subscription is active with: claude /status\n"
        )


_check_no_api_key()


# ── Internal runner ───────────────────────────────────────────────────────────
def _run(prompt: str, extra_flags: list[str] | None = None) -> str:
    """
    Shell out to `claude -p <prompt>` and return stdout.
    Retries up to _MAX_RETRIES times on subprocess error.
    Surfaces rate-limit messages plainly instead of raising.
    """
    cmd = ["claude", "-p", prompt, "--model", MODEL]
    if extra_flags:
        cmd.extend(extra_flags)

    last_error: Exception | None = None
    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=_SUBPROCESS_TIMEOUT,
            )
            if result.returncode == 0:
                return result.stdout.strip()

            stderr = result.stderr.strip()

            # Surface rate-limit messages without a noisy traceback
            if any(phrase in stderr.lower() for phrase in ("rate limit", "429", "too many requests")):
                print(
                    f"\n[llm] Rate limit hit. Claude Pro limits are tighter than Max.\n"
                    f"      Wait a minute, then retry. Details: {stderr}\n"
                )
                return ""

            last_error = RuntimeError(
                f"claude exited {result.returncode}: {stderr or '(no stderr)'}"
            )

        except FileNotFoundError:
            raise RuntimeError(
                "The `claude` CLI was not found on PATH.\n"
                "Install it with: npm install -g @anthropic-ai/claude-code\n"
                "Then authenticate: claude login\n"
                "Confirm subscription is active: claude /status\n"
            ) from None

        except subprocess.TimeoutExpired:
            last_error = RuntimeError(f"claude subprocess timed out after {_SUBPROCESS_TIMEOUT} s")

        except Exception as exc:
            last_error = exc

        if attempt < _MAX_RETRIES:
            print(f"[llm] Transient error (attempt {attempt}/{_MAX_RETRIES}): {last_error}. Retrying in {_RETRY_DELAY}s…")
            time.sleep(_RETRY_DELAY)

    raise RuntimeError(f"claude failed after {_MAX_RETRIES} attempts: {last_error}")


# ── Public helpers ─────────────────────────────────────────────────────────────
def query_text(prompt: str) -> str:
    """Call Claude and return the response as plain text."""
    return _run(prompt)


def query_json(prompt: str, schema_hint: str = "") -> dict | list:
    """
    Call Claude requesting JSON output. Parses the response.
    If parsing fails, sends a repair instruction and retries once.
    Returns the parsed Python object (dict or list).
    """
    json_prompt = prompt
    if schema_hint:
        json_prompt = f"{prompt}\n\nRespond with valid JSON only. Schema: {schema_hint}"
    else:
        json_prompt = f"{prompt}\n\nRespond with valid JSON only. No markdown, no explanation."

    raw = _run(json_prompt, extra_flags=["--output-format", "json"])

    # claude --output-format json wraps the model reply in a JSON envelope;
    # extract the actual text content before parsing as domain JSON.
    raw = _unwrap_cli_json(raw)

    parsed, err = _try_parse(raw)
    if parsed is not None:
        return parsed

    # One repair pass
    repair_prompt = (
        f"The following text was supposed to be valid JSON but failed to parse "
        f"({err}). Return only the corrected JSON, nothing else:\n\n{raw}"
    )
    repaired_raw = _run(repair_prompt, extra_flags=["--output-format", "json"])
    repaired_raw = _unwrap_cli_json(repaired_raw)

    parsed, err2 = _try_parse(repaired_raw)
    if parsed is not None:
        return parsed

    raise ValueError(
        f"Claude returned invalid JSON after repair attempt.\n"
        f"Original error: {err}\n"
        f"Repair error: {err2}\n"
        f"Raw output:\n{raw}\n"
    )


# ── Helpers ───────────────────────────────────────────────────────────────────
def _unwrap_cli_json(raw: str) -> str:
    """
    `claude --output-format json` wraps the response in an envelope like:
        {"type": "result", "result": "...actual text...", ...}
    Extract the inner text if that envelope is present.
    """
    if not raw:
        return raw
    try:
        envelope = json.loads(raw)
        if isinstance(envelope, dict):
            # The model's reply is in "result" for non-streaming output
            if "result" in envelope:
                return str(envelope["result"]).strip()
    except (json.JSONDecodeError, TypeError):
        pass
    return raw


def _try_parse(text: str) -> tuple[dict | list | None, str]:
    """Try to parse text as JSON. Returns (parsed, "") or (None, error_msg)."""
    if not text:
        return None, "empty response"
    # Strip common markdown fences
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    try:
        return json.loads(cleaned), ""
    except json.JSONDecodeError as exc:
        return None, str(exc)
