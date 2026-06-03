"""
Smoke test for the shared/ layer.
Run from the repo root: python test_shared.py

Tests in order:
  1. All imports resolve
  2. Non-Claude helpers work (fetch guard, antislop check, report render, adapters)
  3. One real Claude call via `claude -p` (requires claude on PATH and subscription active)
"""

import sys
import os
from pathlib import Path

# ── Confirm we're in the right place ─────────────────────────────────────────
root = Path(__file__).parent
if not (root / "shared" / "llm.py").exists():
    print("ERROR: run this from the repo root, e.g.  python test_shared.py")
    sys.exit(1)

sys.path.insert(0, str(root))

print("=" * 55)
print("  shared/ smoke test")
print("=" * 55)

# ── 1. Imports ────────────────────────────────────────────────────────────────
print("\n[1] Imports...")
try:
    from shared.llm import query_text, query_json, MODEL
    from shared.fetch import fetch, FetchResult
    from shared.antislop import clean, check
    from shared.report import render, Section
    from shared.adapters.engines import query_engines
    from shared.adapters.search import discover_urls
    from shared.adapters.enrichment import enrich_contact
    print(f"    OK  (model: {MODEL})")
except Exception as exc:
    print(f"    FAIL: {exc}")
    sys.exit(1)

# ── 2. fetch guard ────────────────────────────────────────────────────────────
print("\n[2] fetch: blocked-host guard...")
try:
    fetch("https://www.google.com/search?q=test")
    print("    FAIL: should have raised ValueError")
    sys.exit(1)
except ValueError:
    print("    OK  (google.com blocked as expected)")

# ── 3. fetch: real URL ────────────────────────────────────────────────────────
print("\n[3] fetch: real URL (example.com)...")
result = fetch("https://example.com")
if not result.ok:
    print(f"    FAIL: {result.error}")
    sys.exit(1)
assert "Example Domain" in result.text or result.body, "expected some body text"
print(f"    OK  ({len(result.body)} chars, {len(result.links)} links)")

# ── 4. antislop check ─────────────────────────────────────────────────────────
print("\n[4] antislop: violation detection...")
violations = check("This is a very robust and seamless solution — great leverage!")
if len(violations) == 0:
    print("    FAIL: expected violations, found none")
    sys.exit(1)
print(f"    OK  ({len(violations)} violations detected: {violations[:2]}...)")

# ── 5. report render ──────────────────────────────────────────────────────────
print("\n[5] report: HTML render...")
html = render("Test Report", [Section("Hello", "<p>world</p>")])
assert "<h2>Hello</h2>" in html and "world" in html
print(f"    OK  ({len(html)} chars of HTML)")

# ── 6. adapters ───────────────────────────────────────────────────────────────
print("\n[6] adapters: manual defaults...")
urls = discover_urls("test query", manual_urls=["https://example.com"])
assert urls == ["https://example.com"]
contact = enrich_contact({"name": "Ada", "company": "Acme"})
assert contact["name"] == "Ada"
print("    OK  (search and enrichment return manual data)")

# ── 7. Claude call ────────────────────────────────────────────────────────────
print("\n[7] Claude: one real text call via `claude -p`...")
print("    (this requires `claude` on PATH and an active subscription)")
try:
    answer = query_text("Reply with exactly three words: shared layer works")
    if not answer.strip():
        print("    WARN: got empty response (rate limit?)")
    else:
        print(f"    OK  response: \"{answer.strip()[:80]}\"")
except RuntimeError as exc:
    print(f"    FAIL: {exc}")
    sys.exit(1)

# ── 8. Claude JSON call ───────────────────────────────────────────────────────
print("\n[8] Claude: one real JSON call via `claude -p --output-format json`...")
try:
    data = query_json(
        'Return a JSON object with one key "status" and value "ok".',
        schema_hint='{"status": "string"}',
    )
    assert isinstance(data, dict), f"expected dict, got {type(data)}"
    print(f"    OK  response: {data}")
except Exception as exc:
    print(f"    FAIL: {exc}")
    sys.exit(1)

print("\n" + "=" * 55)
print("  All checks passed. shared/ layer is ready.")
print("=" * 55 + "\n")
