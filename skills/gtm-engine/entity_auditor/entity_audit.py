"""
entity_audit.py — audit a brand's entity authority and generate fix assets.

Usage:
    python entity_auditor/entity_audit.py --brand "Acme" --url "https://acme.com"
    python entity_auditor/entity_audit.py --brand "Acme" --url "https://acme.com" --about-url "https://acme.com/about"

Outputs (written to outputs/<brand-slug>/):
    report.html          — self-contained HTML audit report
    organization.jsonld  — ready-to-paste Organization schema

Run from the repo root. Authenticate first: claude login && claude /status
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
from datetime import date
from pathlib import Path

# ── Repo root on path so shared/ imports work from any cwd ───────────────────
_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from shared.antislop import clean as antislop_clean
from shared.fetch import fetch, FetchResult
from shared.llm import query_json, query_text
from shared.report import Section, render
from entity_auditor.sources.wikidata import lookup as wikidata_lookup

_ANTISLOP_RULES = _REPO_ROOT / "antislop_rules.md"

# Grade thresholds (total out of 40)
_GRADES = [
    (34, "A"),
    (28, "B"),
    (20, "C"),
    (12, "D"),
    (0,  "F"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = _parse_args()
    brand: str = args.brand
    homepage_url: str = args.url.rstrip("/")
    about_url_override: str | None = args.about_url

    out_dir = _REPO_ROOT / "outputs" / _slug(brand)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'─'*60}")
    print(f"  Entity audit: {brand}")
    print(f"  {homepage_url}")
    print(f"{'─'*60}\n")

    # ── Stage 1: on-site signals ─────────────────────────────────────────────
    print("[1/5] Fetching on-site signals...")
    homepage = fetch(homepage_url)
    if not homepage.ok:
        print(f"      ERROR: could not fetch homepage: {homepage.error}")
        sys.exit(1)
    print(f"      Homepage: {homepage_url} ✓")

    about_url = about_url_override or _discover_about_url(homepage, homepage_url)
    about: FetchResult | None = None
    if about_url:
        about = fetch(about_url)
        if about.ok:
            print(f"      About page: {about_url} ✓" + (" (auto-discovered)" if not about_url_override else ""))
        else:
            print(f"      About page: {about_url} — fetch failed ({about.error}), skipping")
            about = None
    else:
        print("      About page: not found in nav (pass --about-url to specify one)")

    on_site = _analyse_on_site(brand, homepage, about)
    _print_on_site_summary(on_site)

    # ── Stage 2: Wikidata ────────────────────────────────────────────────────
    print("\n[2/5] Checking Wikidata...")
    wikidata = wikidata_lookup(brand, homepage_url)
    if wikidata.error:
        print(f"      Wikidata check failed: {wikidata.error} (continuing without it)")
    elif wikidata.found:
        print(f"      Entity found: {wikidata.entity_id} ({wikidata.label})")
        if wikidata.description:
            print(f"      Description: \"{wikidata.description}\"")
    else:
        print("      No Wikidata entity found for this brand")

    # ── Stage 3: Scoring ─────────────────────────────────────────────────────
    print("\n[3/5] Scoring entity footprint with Claude...")
    audit_data = _build_audit_data(brand, homepage_url, on_site, wikidata)
    scores = _score(brand, audit_data)
    _print_scores(scores)

    # Pass Claude's explanations through the anti-slop gate
    for dim in scores["dimensions"].values():
        dim["explanation"] = antislop_clean(dim["explanation"], _ANTISLOP_RULES)
    scores["headline"] = antislop_clean(scores["headline"], _ANTISLOP_RULES)

    # ── Stage 4: Fix assets ───────────────────────────────────────────────────
    print("\n[4/5] Generating fix assets...")
    jsonld_block = _generate_jsonld(brand, homepage_url, on_site, wikidata, scores)
    entity_description = antislop_clean(
        _generate_entity_description(brand, audit_data), _ANTISLOP_RULES
    )
    directory_list = antislop_clean(
        _generate_directory_list(brand, audit_data), _ANTISLOP_RULES
    )
    print("      ✓ Organization JSON-LD")
    print("      ✓ Entity description")
    print("      ✓ Directory recommendations")

    # ── Stage 5: Write outputs ────────────────────────────────────────────────
    print("\n[5/5] Writing report...")
    jsonld_path = out_dir / "organization.jsonld"
    jsonld_path.write_text(json.dumps(jsonld_block, indent=2), encoding="utf-8")

    report_html = _build_report(
        brand=brand,
        homepage_url=homepage_url,
        scores=scores,
        on_site=on_site,
        wikidata=wikidata,
        jsonld_block=jsonld_block,
        entity_description=entity_description,
        directory_list=directory_list,
    )
    report_path = out_dir / "report.html"
    report_path.write_text(report_html, encoding="utf-8")

    print(f"\n{'─'*60}")
    print(f"  Report:     {report_path}")
    print(f"  JSON-LD:    {jsonld_path}")
    print(f"{'─'*60}")
    print("\n  Next step: validate the JSON-LD at")
    print("  https://search.google.com/test/rich-results")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: on-site analysis
# ─────────────────────────────────────────────────────────────────────────────

def _discover_about_url(homepage: FetchResult, base_url: str) -> str | None:
    """Scan homepage links for an about / company / story page on the same domain."""
    base_host = urllib.parse.urlparse(base_url).hostname or ""
    patterns = re.compile(
        r"/(about|company|story|team|who-we-are|our-story|mission|us)(/|$|\?)",
        re.IGNORECASE,
    )
    for link in homepage.links:
        parsed = urllib.parse.urlparse(link)
        if (parsed.hostname or "").removeprefix("www.") == base_host.removeprefix("www."):
            if patterns.search(parsed.path):
                return link
    return None


def _analyse_on_site(brand: str, homepage: FetchResult, about: FetchResult | None) -> dict:
    """Extract entity signals from on-site pages."""
    all_jsonld: list[dict] = list(homepage.jsonld)
    if about:
        all_jsonld.extend(about.jsonld)

    org_schema = _find_org_schema(all_jsonld)
    same_as = org_schema.get("sameAs", []) if org_schema else []
    if isinstance(same_as, str):
        same_as = [same_as]

    # Social links in footer / nav (links to known social domains)
    social_links = _extract_social_links(homepage.links + (about.links if about else []))

    # Description signals: og:description, meta description — approximated from body text
    body_snippet = (homepage.body or "")[:2000]
    about_snippet = ((about.body if about else "") or "")[:2000]

    # H1 tags as brand description signal
    h1s = [h["text"] for h in homepage.headings if h["level"] == 1]

    return {
        "org_schema_found": org_schema is not None,
        "org_schema": org_schema or {},
        "same_as_in_schema": same_as,
        "all_jsonld_types": list({s.get("@type", "") for s in all_jsonld if s.get("@type")}),
        "social_links_found": social_links,
        "h1s": h1s,
        "homepage_snippet": body_snippet,
        "about_snippet": about_snippet,
        "pages_fetched": ["homepage"] + (["about"] if about else []),
    }


def _find_org_schema(jsonld_blocks: list[dict]) -> dict | None:
    for block in jsonld_blocks:
        t = block.get("@type", "")
        if isinstance(t, str) and t in ("Organization", "Corporation", "LocalBusiness"):
            return block
        if isinstance(t, list) and any(v in t for v in ("Organization", "Corporation")):
            return block
    return None


def _extract_social_links(links: list[str]) -> dict[str, str]:
    patterns = {
        "twitter": re.compile(r"twitter\.com/(?!share|intent)([^/?#]+)"),
        "linkedin": re.compile(r"linkedin\.com/(?:company/|in/|pub/)([^/?#]+)"),
        "facebook": re.compile(r"facebook\.com/([^/?#]+)"),
        "youtube": re.compile(r"youtube\.com/(?:c/|channel/|@)([^/?#]+)"),
        "github": re.compile(r"github\.com/([^/?#]+)"),
        "instagram": re.compile(r"instagram\.com/([^/?#]+)"),
        "discord": re.compile(r"discord\.(?:gg|com/invite)/([^/?#]+)"),
    }
    found: dict[str, str] = {}
    for link in links:
        for platform, pattern in patterns.items():
            if platform not in found:
                m = pattern.search(link)
                if m:
                    found[platform] = link
    return found


def _print_on_site_summary(on_site: dict) -> None:
    schema_types = ", ".join(on_site["all_jsonld_types"]) or "none"
    print(f"      JSON-LD types found: {schema_types}")
    print(f"      Organization schema: {'✓ found' if on_site['org_schema_found'] else '✗ missing'}")
    same_as = on_site["same_as_in_schema"]
    print(f"      sameAs links in schema: {len(same_as)}")
    socials = list(on_site["social_links_found"].keys())
    print(f"      Social links in page: {', '.join(socials) or 'none detected'}")


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: scoring
# ─────────────────────────────────────────────────────────────────────────────

def _build_audit_data(
    brand: str,
    homepage_url: str,
    on_site: dict,
    wikidata,
) -> dict:
    return {
        "brand": brand,
        "homepage_url": homepage_url,
        "on_site": {
            "organization_schema_found": on_site["org_schema_found"],
            "same_as_links_in_schema": on_site["same_as_in_schema"],
            "jsonld_types_present": on_site["all_jsonld_types"],
            "social_links_detected": list(on_site["social_links_found"].keys()),
            "pages_fetched": on_site["pages_fetched"],
            "homepage_text_snippet": on_site["homepage_snippet"][:800],
            "about_page_text_snippet": on_site["about_snippet"][:800],
            "h1_headings": on_site["h1s"],
        },
        "wikidata": wikidata.summary() if wikidata else {"found": False},
    }


def _score(brand: str, audit_data: dict) -> dict:
    prompt = f"""You are auditing the entity authority of "{brand}" for AI engine visibility.

Entity authority measures how recognizable a brand is to AI engines as a distinct,
well-defined entity. AI engines cite brands they can identify and independently verify.

AUDIT DATA:
{json.dumps(audit_data, indent=2)}

Score each of the four dimensions from 0 to 10. Be specific. Name what was found and what
is missing. Do not use filler language. Each explanation should be 2-4 plain sentences.

Dimension definitions:
- entity_presence: Does the brand exist as a named entity in third-party databases (Wikidata,
  industry directories)? Is it findable by name independently of its own site?
- description_consistency: Does the brand describe itself the same way across its own pages and
  any third-party sources? Is the description clear, specific, and attributable?
- structured_data: Does the site have an Organization schema? Does it include a description,
  url, logo, and sameAs links? Are the types correct?
- third_party_corroboration: How many independent authoritative sources (beyond the brand's
  own site) mention or define it? Social profiles, Wikidata, press, directories?

Grade mapping: A=34-40, B=28-33, C=20-27, D=12-19, F=0-11

Return ONLY valid JSON with this exact structure:
{{
  "dimensions": {{
    "entity_presence": {{
      "score": <integer 0-10>,
      "label": "Entity Presence",
      "explanation": "<2-4 sentences, plain language, specific>"
    }},
    "description_consistency": {{
      "score": <integer 0-10>,
      "label": "Description Consistency",
      "explanation": "<2-4 sentences>"
    }},
    "structured_data": {{
      "score": <integer 0-10>,
      "label": "Structured Data",
      "explanation": "<2-4 sentences>"
    }},
    "third_party_corroboration": {{
      "score": <integer 0-10>,
      "label": "Third-Party Corroboration",
      "explanation": "<2-4 sentences>"
    }}
  }},
  "total": <sum of four scores, integer>,
  "grade": "<A|B|C|D|F>",
  "headline": "<one sentence: the single most important gap to fix>"
}}"""

    result = query_json(prompt)

    # Validate and clamp scores
    total = 0
    for dim in result.get("dimensions", {}).values():
        score = max(0, min(10, int(dim.get("score", 0))))
        dim["score"] = score
        total += score
    result["total"] = total
    result["grade"] = _letter_grade(total)

    return result


def _letter_grade(total: int) -> str:
    for threshold, grade in _GRADES:
        if total >= threshold:
            return grade
    return "F"


def _print_scores(scores: dict) -> None:
    for key, dim in scores.get("dimensions", {}).items():
        label = dim.get("label", key)
        score = dim.get("score", "?")
        print(f"      {label:<30} {score}/10")
    total = scores.get("total", "?")
    grade = scores.get("grade", "?")
    print(f"      {'─'*38}")
    print(f"      {'Overall':<30} {total}/40  (Grade: {grade})")


# ─────────────────────────────────────────────────────────────────────────────
# Stage 4: fix assets
# ─────────────────────────────────────────────────────────────────────────────

def _generate_jsonld(brand: str, homepage_url: str, on_site: dict, wikidata, scores: dict) -> dict:
    known_same_as = list(on_site["same_as_in_schema"])
    if wikidata.found:
        for url in wikidata.same_as_urls():
            if url not in known_same_as:
                known_same_as.append(url)

    # Exclude invite/community links that aren't authoritative entity URLs
    _SAME_AS_EXCLUDE = {"discord"}
    social_links = {
        k: v for k, v in on_site["social_links_found"].items()
        if k not in _SAME_AS_EXCLUDE
    }

    prompt = f"""Generate a valid Organization schema.org JSON-LD block for "{brand}".

Known data:
- Homepage URL: {homepage_url}
- Verified sameAs URLs: {json.dumps(known_same_as)}
- Social profiles found on site: {json.dumps(social_links)}
- Wikidata entry: {wikidata.entity_url if wikidata.found else "none"}
- Existing schema on site: {json.dumps(on_site['org_schema']) if on_site['org_schema_found'] else "none"}

Rules:
- @context must be "https://schema.org"
- @type must be "Organization"
- Include: name, url, description, logo (use "{homepage_url}/favicon.ico" as placeholder if unknown)
- sameAs: include all verified URLs above, plus placeholder strings in square brackets for
  common directories where this brand is not yet verified. Use format: "[CRUNCHBASE_URL]",
  "[G2_PROFILE_URL]", "[LINKEDIN_COMPANY_URL]", "[GLASSDOOR_URL]" — only if not already in
  verified list.
- Do NOT invent a real URL for a profile that has not been verified. Use the bracket placeholder.
- If a field value is unknown, omit it or use null. Do not invent data.

Return ONLY the JSON-LD object. No markdown fences. No explanation."""

    result = query_json(prompt)

    # Ensure mandatory fields
    result.setdefault("@context", "https://schema.org")
    result.setdefault("@type", "Organization")
    result.setdefault("name", brand)
    result.setdefault("url", homepage_url)

    return result


def _generate_entity_description(brand: str, audit_data: dict) -> str:
    prompt = f"""Write a one-paragraph entity description for "{brand}" suitable for a Wikidata
entry and for reuse across directories and press releases.

Available data:
{json.dumps(audit_data, indent=2)}

Requirements:
- 2-4 sentences.
- Third-person, encyclopedic tone. No marketing language.
- State: what the company does, who it serves, founding year if known.
- If a fact cannot be verified from the data provided, use [PLACEHOLDER: fact] rather than
  inventing it.
- Do not use em dashes, filler openers, or hollow intensifiers.

Return only the paragraph. No preamble, no heading."""

    return query_text(prompt)


def _generate_directory_list(brand: str, audit_data: dict) -> str:
    on_site = audit_data.get("on_site", {})
    brand_context = (
        f"Brand: {brand}. "
        f"Known social presence: {', '.join(on_site.get('social_links_detected', [])) or 'minimal'}. "
        f"Wikidata: {'found' if audit_data.get('wikidata', {}).get('found') else 'not found'}."
    )

    prompt = f"""List the 10 most authoritative directories and sources where a B2B SaaS brand
should be listed to improve its entity authority with AI engines.

Context: {brand_context}

Prioritize sources that:
1. AI engines (ChatGPT, Claude, Perplexity, Gemini) are known to reference in their training data
2. Provide structured entity data (not just backlinks)
3. Are free or low-cost to claim

For each source, give:
- Name and URL format
- One sentence on why it matters for entity authority
- Status: indicate if already present based on context, otherwise "not verified"

Format as a numbered list. Start with the highest-impact source. No preamble."""

    return query_text(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# Report assembly
# ─────────────────────────────────────────────────────────────────────────────

def _build_report(
    brand: str,
    homepage_url: str,
    scores: dict,
    on_site: dict,
    wikidata,
    jsonld_block: dict,
    entity_description: str,
    directory_list: str,
) -> str:
    grade = scores.get("grade", "?")
    total = scores.get("total", 0)
    headline = scores.get("headline", "")

    sections = [
        _section_score(scores, brand),
        _section_signals(on_site, wikidata),
        _section_gaps(scores),
        _section_entity_description(entity_description),
        _section_jsonld(jsonld_block),
        _section_directories(directory_list),
    ]

    return render(
        title=f"Entity Audit: {brand}",
        subtitle=f"Audited {date.today().isoformat()} · {homepage_url}",
        sections=sections,
    )


def _section_score(scores: dict, brand: str) -> Section:
    grade = scores.get("grade", "?")
    total = scores.get("total", 0)
    headline = html.escape(scores.get("headline", ""))

    grade_color = {
        "A": "#065f46", "B": "#1e40af", "C": "#92400e", "D": "#9d174d", "F": "#991b1b"
    }.get(grade, "#333")

    dims_html = ""
    for dim in scores.get("dimensions", {}).values():
        score = dim["score"]
        label = html.escape(dim["label"])
        pct = int(score / 10 * 100)
        bar_color = "#065f46" if score >= 8 else "#1e40af" if score >= 6 else "#92400e" if score >= 4 else "#991b1b"
        dims_html += f"""
<div style="margin-bottom:1rem;">
  <div style="display:flex;justify-content:space-between;margin-bottom:.3rem;">
    <span style="font-weight:600;">{label}</span>
    <span style="font-weight:700;color:{bar_color};">{score}/10</span>
  </div>
  <div style="background:#e8e8e4;border-radius:3px;height:8px;">
    <div style="width:{pct}%;background:{bar_color};height:8px;border-radius:3px;"></div>
  </div>
</div>"""

    content = f"""
<div style="display:flex;align-items:center;gap:2rem;margin-bottom:1.5rem;">
  <div class="score-badge" style="font-size:2.8rem;color:{grade_color};">{grade}</div>
  <div>
    <div style="font-size:1.1rem;font-weight:700;">{total}/40</div>
    <div style="color:#666;font-size:.9rem;">{html.escape(headline)}</div>
  </div>
</div>
{dims_html}"""

    return Section("Score", content)


def _section_signals(on_site: dict, wikidata) -> Section:
    def tick(val: bool) -> str:
        return "✓" if val else "✗"

    rows = [
        ("Organization schema on site", tick(on_site["org_schema_found"])),
        ("sameAs links in schema", str(len(on_site["same_as_in_schema"])) + (" link(s)" if on_site["same_as_in_schema"] else " (none)")),
        ("Social profiles on site", ", ".join(on_site["social_links_found"]) or "none detected"),
        ("Wikidata entity", tick(wikidata.found) + (f" ({wikidata.entity_id}: {html.escape(wikidata.label)})" if wikidata.found else " (no entry found)")),
        ("Wikidata description", html.escape(wikidata.description) if wikidata.found and wikidata.description else "(none)"),
        ("JSON-LD types on site", html.escape(", ".join(on_site["all_jsonld_types"])) or "none"),
    ]

    rows_html = "\n".join(
        f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>"
        for k, v in rows
    )
    content = f"""
<table>
<thead><tr><th>Signal</th><th>Finding</th></tr></thead>
<tbody>
{rows_html}
</tbody>
</table>"""

    return Section("Signals Found", content)


def _section_gaps(scores: dict) -> Section:
    items = ""
    for dim in scores.get("dimensions", {}).values():
        score = dim["score"]
        label = html.escape(dim["label"])
        explanation = html.escape(dim["explanation"])
        severity = "gap" if score < 5 else "warm" if score < 8 else "ok"
        items += f"""
<div style="margin-bottom:1.2rem;padding:1rem;background:#f8f8f6;border-radius:4px;border-left:4px solid {'#991b1b' if severity=='gap' else '#92400e' if severity=='warm' else '#065f46'};">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.4rem;">
    <strong>{label}</strong>
    <span class="tag tag-{'gap' if severity=='gap' else 'warm' if severity=='warm' else 'ok'}">{score}/10</span>
  </div>
  <p style="margin:0;font-size:.95rem;">{explanation}</p>
</div>"""

    return Section("Gap Analysis", items)


def _section_entity_description(description: str) -> Section:
    content = f"""
<div class="notice">Use this text verbatim on your Wikidata entry, About page, Crunchbase profile,
and any directory that asks for a company description. Consistent wording across sources
strengthens your entity signal. Replace any [PLACEHOLDER] before publishing.</div>
<p style="background:#f8f8f6;padding:1rem;border-radius:4px;font-style:italic;">{html.escape(description)}</p>"""
    return Section("Entity Description", content)


def _section_jsonld(jsonld_block: dict) -> Section:
    pretty = html.escape(json.dumps(jsonld_block, indent=2))
    content = f"""
<div class="notice">
  Paste this into your homepage <code>&lt;head&gt;</code>. Replace any bracketed placeholders
  with verified URLs before deploying. Validate at
  <a href="https://search.google.com/test/rich-results" target="_blank">Google Rich Results Test</a>.
</div>
<pre><code>{pretty}</code></pre>"""
    return Section("Organization JSON-LD", content)


def _section_directories(directory_list: str) -> Section:
    # Convert plain text list to HTML paragraphs
    paragraphs = "\n".join(
        f"<p>{html.escape(line)}</p>" if line.strip() else ""
        for line in directory_list.splitlines()
    )
    content = f"""
<div class="notice">Claim each listing in order. The first three have the most impact on
AI engine entity recognition.</div>
{paragraphs}"""
    return Section("Recommended Directories", content)


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit a brand's entity authority and generate fix assets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python entity_auditor/entity_audit.py --brand "Acme" --url "https://acme.com"
  python entity_auditor/entity_audit.py --brand "Acme" --url "https://acme.com" --about-url "https://acme.com/about"
""",
    )
    parser.add_argument("--brand", required=True, help="Brand name, e.g. 'Acme Corp'")
    parser.add_argument("--url", required=True, help="Homepage URL, e.g. 'https://acme.com'")
    parser.add_argument(
        "--about-url",
        default=None,
        help="About page URL (optional; auto-discovered from homepage nav if omitted)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
