"""
research.py — generate the front end of a peer research report.

Usage:
    python research_engine/research.py --input research_engine/samples/brief_input.md
    python research_engine/research.py --input research_engine/samples/brief_input.md \\
        --contributors research_engine/samples/contributors.csv

Outputs (written to outputs/research_engine/<slug>/):
    report_package.md   — insight angle, survey, outline, and contributor invitations

Run from the repo root. Authenticate first: claude login && claude /status
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import date
from pathlib import Path

_REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from shared.antislop import clean as antislop_clean
from shared.fetch import fetch
from shared.llm import query_json, query_text
from shared.adapters.enrichment import enrich_contact

_ANTISLOP_RULES = _REPO_ROOT / "antislop_rules.md"


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    args = _parse_args()

    print(f"\n{'─'*60}")
    print("  Research Engine")
    print(f"{'─'*60}\n")

    # Stage 1: Load inputs
    print("[1/5] Loading inputs...")
    inputs = _load_input(args.input)
    category = inputs["category"]
    company_ctx = inputs["company"]
    icp_ctx = inputs.get("icp", "")
    ref_urls = inputs.get("reference_urls", [])

    print(f"      Category: {category[:70]}{'…' if len(category) > 70 else ''}")
    print(f"      Company:  {company_ctx[:70]}{'…' if len(company_ctx) > 70 else ''}")
    print(f"      Reference URLs: {len(ref_urls)}")

    if args.contributors:
        contributors = _load_contributors_csv(args.contributors)
        print(f"      Contributors: {len(contributors)} loaded from {args.contributors}")
    else:
        contributors = _prompt_contributors()

    # Stage 2: Fetch references and synthesize angle
    print("\n[2/5] Fetching references and synthesizing insight angle...")
    refs_content = _fetch_references(ref_urls)
    angles = _synthesize_angle(category, company_ctx, icp_ctx, refs_content)
    _print_angles(angles)

    # Stage 3: Survey design
    print("\n[3/5] Designing survey questionnaire...")
    survey = _design_survey(category, angles, icp_ctx)
    q_count = len(survey.get("questions", []))
    print(f"      {q_count} questions generated")

    # Stage 4: Report outline
    print("\n[4/5] Building report outline...")
    outline = _build_outline(category, company_ctx, icp_ctx, angles)
    print("      Outline complete")

    # Stage 5: Contributor invitations
    print(f"\n[5/5] Writing {len(contributors)} contributor invitation(s)...")
    invites = []
    for i, contrib in enumerate(contributors, 1):
        name = contrib.get("name", "?")
        company = contrib.get("company", "?")
        print(f"      [{i}/{len(contributors)}] {name} at {company}...")
        enriched = enrich_contact(contrib)
        invite_text = _write_invite(enriched, category, angles, company_ctx)
        invites.append({"contributor": enriched, "invite": invite_text})

    # Write output
    slug = _slug(category)
    out_dir = _REPO_ROOT / "outputs" / "research_engine" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    output_path = out_dir / "report_package.md"
    content = _render_markdown(category, angles, survey, outline, invites)
    output_path.write_text(content, encoding="utf-8")

    print(f"\n{'─'*60}")
    print(f"  Output: {output_path}")
    print(f"{'─'*60}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Input loading
# ─────────────────────────────────────────────────────────────────────────────

def _load_input(path: str) -> dict:
    """Parse a markdown brief input file into sections."""
    p = Path(path)
    if not p.exists():
        print(f"ERROR: input file not found: {path}")
        sys.exit(1)

    text = p.read_text(encoding="utf-8")
    sections: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_key:
                sections[current_key] = "\n".join(current_lines).strip()
            heading = line[3:].strip().lower()
            heading = re.sub(r"\s*\(optional\)\s*", "", heading).strip()
            current_key = heading
            current_lines = []
        else:
            if current_key:
                current_lines.append(line)

    if current_key:
        sections[current_key] = "\n".join(current_lines).strip()

    ref_section = sections.get("reference urls", "")
    ref_urls = [
        line.strip()
        for line in ref_section.splitlines()
        if line.strip().startswith("http")
    ]

    category_key = next((k for k in sections if "category" in k), "")
    company_key = next((k for k in sections if "company" in k), "")
    icp_key = next((k for k in sections if "icp" in k), "")

    if not category_key or not sections.get(category_key):
        print("ERROR: input file must have a '## Category and theme' section with content.")
        sys.exit(1)
    if not company_key or not sections.get(company_key):
        print("ERROR: input file must have a '## Company running the research' section with content.")
        sys.exit(1)

    return {
        "category": sections[category_key],
        "company": sections[company_key],
        "icp": sections.get(icp_key, "") if icp_key else "",
        "reference_urls": ref_urls,
    }


def _load_contributors_csv(path: str) -> list[dict]:
    """Load contributors from a CSV file with columns: name, role, company, public_url."""
    p = Path(path)
    if not p.exists():
        print(f"ERROR: contributors file not found: {path}")
        sys.exit(1)

    contributors = []
    with p.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            c = {
                "name": (row.get("name") or "").strip(),
                "title": (row.get("role") or row.get("title") or "").strip(),
                "company": (row.get("company") or "").strip(),
                "url": (row.get("public_url") or row.get("url") or "").strip(),
                "notes": (row.get("notes") or "").strip(),
            }
            if c["name"] and c["company"]:
                contributors.append(c)

    return contributors


def _prompt_contributors() -> list[dict]:
    """Interactively collect contributor info one at a time."""
    print("\n  Add target contributors (leave Name blank to finish):\n")
    contributors = []
    i = 1
    while True:
        print(f"  Contributor {i}:")
        name = input("    Name (or Enter to finish): ").strip()
        if not name:
            break
        company = input("    Company: ").strip()
        title = input("    Title/Role (optional): ").strip()
        url = input("    Public URL — company page or article (optional): ").strip()
        notes = input("    Notes — anything specific that helps personalize the invite (optional): ").strip()

        if not company:
            print("    (Company is required. Skipping this entry.)")
            continue

        contributors.append({
            "name": name,
            "company": company,
            "title": title,
            "url": url,
            "notes": notes,
        })
        i += 1

    if not contributors:
        print("\n  No contributors added. The output will include all sections except invitations.")

    return contributors


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: reference fetching and angle synthesis
# ─────────────────────────────────────────────────────────────────────────────

def _fetch_references(urls: list[str]) -> str:
    """Fetch each reference URL and return concatenated text content."""
    if not urls:
        return ""

    chunks = []
    for url in urls:
        print(f"      Fetching: {url}")
        try:
            result = fetch(url)
        except ValueError as exc:
            print(f"      ✗ Blocked: {exc}")
            continue

        if result.ok:
            snippet = result.body[:3000]
            chunks.append(f"Source: {url}\n{snippet}")
            print(f"      ✓ {len(result.body)} chars")
        else:
            print(f"      ✗ Failed: {result.error}")

    return "\n\n---\n\n".join(chunks)


def _synthesize_angle(
    category: str,
    company_ctx: str,
    icp_ctx: str,
    refs_content: str,
) -> dict:
    """Ask Claude for a defensible angle and a contrarian alternative."""
    refs_block = (
        f"\nReference material (synthesize these; do not copy them verbatim):\n{refs_content[:6000]}"
        if refs_content
        else "\n(No reference URLs were provided. Generate angles from the category alone.)"
    )

    prompt = f"""You are designing a peer research report for a B2B company. Identify the two
strongest research angles for this category.

Category / theme:
{category}

Company running the research:
{company_ctx}

Target respondents:
{icp_ctx if icp_ctx else "B2B marketing and growth leaders"}
{refs_block}

Produce two angles:

DEFENSIBLE ANGLE — the most credible, evidence-grounded take. Name the specific tension
or gap you are documenting. Be concrete about what you would measure and what a surprising
finding would look like. This angle should survive scrutiny from a skeptical practitioner.

CONTRARIAN ALTERNATIVE — the bolder counter-narrative to the conventional wisdom in this
space. What does the available data (or the absence of it) actually suggest that most
practitioners are not yet saying aloud? Higher risk, higher reward.

For each angle:
- "question": the core research question in one sentence
- "hypothesis": a falsifiable one-sentence hypothesis (e.g., "We expect that X% of companies
  do Y but only Z% see the result they expect")
- "hook": why this angle earns genuine attention from practitioners — not from marketers
  (2-3 sentences, no filler, specific)
- "credibility": what makes this angle defensible and hard to dismiss (2-3 sentences)

Return only valid JSON. No markdown fences. No explanation outside the JSON.
Schema:
{{
  "defensible": {{"question": "", "hypothesis": "", "hook": "", "credibility": ""}},
  "contrarian": {{"question": "", "hypothesis": "", "hook": "", "credibility": ""}}
}}"""

    return query_json(prompt)


def _print_angles(angles: dict) -> None:
    d = angles.get("defensible", {})
    c = angles.get("contrarian", {})
    print(f"\n      Defensible: {d.get('question', '(missing)')[:90]}")
    print(f"      Contrarian: {c.get('question', '(missing)')[:90]}")


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3: survey design
# ─────────────────────────────────────────────────────────────────────────────

def _design_survey(category: str, angles: dict, icp_ctx: str) -> dict:
    """Generate a questionnaire engineered to surface quotable statistics."""
    d = angles.get("defensible", {})
    c = angles.get("contrarian", {})

    prompt = f"""Design a survey questionnaire for a peer research report.

Topic: {category}

Primary angle: {d.get("question", "")}
Primary hypothesis: {d.get("hypothesis", "")}
Contrarian angle to test: {c.get("question", "")}

Target respondents: {icp_ctx if icp_ctx else "B2B marketing and growth leaders"}

Requirements:
- 8 to 12 questions total
- 2 to 3 context questions (role, company size, frequency of a behavior) to segment
  results and validate the respondent fits the ICP
- 4 to 5 quantitative questions designed to produce one or two headline statistics;
  each should either confirm or challenge the primary hypothesis
- 2 to 3 open-ended questions short enough that a busy VP will answer them (one sentence
  is a valid answer); these exist to produce direct quotes for the report
- 1 question that directly tests the contrarian angle
- Every question must be unambiguous and answerable without industry jargon

For multiple_choice questions, include 4 to 5 answer options.
For scale questions, label the endpoints explicitly (e.g., 1 = never, 5 = always).
For percentage questions, note the prompt format (e.g., "Approximately what % of your
budget goes to X?").

Return only valid JSON. No markdown fences.
Schema:
{{
  "questions": [
    {{
      "number": 1,
      "type": "multiple_choice | scale_1_5 | percentage | frequency | open_ended",
      "question": "...",
      "options": ["..."],
      "purpose": "context | stat | quote | contrarian_test"
    }}
  ]
}}"""

    return query_json(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# Stage 4: report outline
# ─────────────────────────────────────────────────────────────────────────────

def _build_outline(
    category: str,
    company_ctx: str,
    icp_ctx: str,
    angles: dict,
) -> str:
    """Generate a structured report outline in markdown."""
    d = angles.get("defensible", {})
    c = angles.get("contrarian", {})

    prompt = f"""Write a detailed outline for a peer research report.

Topic: {category}
Company publishing the report: {company_ctx}
Target readers: {icp_ctx if icp_ctx else "B2B marketing and growth leaders"}

Primary research angle: {d.get("question", "")}
Hypothesis: {d.get("hypothesis", "")}
Contrarian angle to test: {c.get("question", "")}

Produce a report structure that:
- Opens with the central finding as the hook (methodology comes later, not first)
- Contains 3 to 5 main sections, each anchored by a specific survey data point
- Marks where proprietary survey data slots in with: [SURVEY DATA: brief description]
- Marks where contributor quotes slot in with: [CONTRIBUTOR QUOTE: topic]
- Includes a Methodology section (sample size, survey dates, respondent breakdown)
- Includes a Contributors section (to acknowledge the practitioners who participated)
- Ends with 3 to 5 specific, actionable recommendations — not generic advice

For each section, provide:
- A section title
- One sentence on the core argument
- What data or evidence the section needs (reference survey question topics or write [PLACEHOLDER])
- Estimated word count: short (~300 words), medium (~600 words), or long (~1,000 words)

Write in structured markdown. Use ## for main sections, ### for subsections.
Start directly with the outline. No preamble, no closing remarks."""

    return query_text(prompt)


# ─────────────────────────────────────────────────────────────────────────────
# Stage 5: contributor invitations
# ─────────────────────────────────────────────────────────────────────────────

def _write_invite(
    contributor: dict,
    category: str,
    angles: dict,
    company_ctx: str,
) -> str:
    """Generate and antislop a personalized contributor invitation."""
    name = contributor.get("name", "")
    title = contributor.get("title", "")
    company = contributor.get("company", "")
    url = contributor.get("url", "")
    notes = contributor.get("notes", "")

    page_context = _fetch_contributor_page(url)

    d = angles.get("defensible", {})

    prompt = f"""Write a short outreach email inviting a practitioner to contribute to a
peer research report. This is not a sales email. The only ask is a short survey.

Recipient:
- Name: {name}
- Title: {title or "not provided"}
- Company: {company}
- Notes: {notes or "none provided"}
{page_context}

Research details:
- Topic: {category}
- Core research question: {d.get("question", "")}
- Company conducting the research: {company_ctx}

Write an email that:
- Opens with one specific, accurate observation about the recipient's work or their
  company — not a generic compliment ("I admire your work")
- States the research topic and why their perspective would make the data stronger
  (one sentence)
- Makes a single, concrete ask: complete a short practitioner survey (under 8 minutes)
- Offers to share the full report with them before it is published
- Stays under 130 words
- Reads like a message from a person, not a marketing department

Do not:
- Pitch any product or service
- Use hollow openers or compliments
- End with "looking forward to hearing from you" or a similar filler closer

Return only the email body. No subject line. No sign-off line. No preamble."""

    draft = query_text(prompt)
    return antislop_clean(draft, _ANTISLOP_RULES)


def _fetch_contributor_page(url: str) -> str:
    """Attempt to fetch a contributor's public page for personalization context."""
    if not url:
        return ""

    try:
        result = fetch(url)
    except ValueError:
        # Blocked host (e.g. LinkedIn — fetch.py guards against it)
        return ""

    if not result.ok:
        return ""

    snippet = result.body[:1500].strip()
    return f"\nPublic page content (use for personalisation only; do not reproduce verbatim):\n{snippet}"


# ─────────────────────────────────────────────────────────────────────────────
# Output rendering
# ─────────────────────────────────────────────────────────────────────────────

def _render_markdown(
    category: str,
    angles: dict,
    survey: dict,
    outline: str,
    invites: list[dict],
) -> str:
    """Assemble the full output markdown package."""
    today = date.today().isoformat()
    d = angles.get("defensible", {})
    c = angles.get("contrarian", {})

    lines: list[str] = [
        f"# Research Report Package",
        f"",
        f"**Topic:** {category}",
        f"**Generated:** {today} · research_engine",
        "",
        "---",
        "",
        "## 1. Insight Angle",
        "",
        "### Defensible Angle",
        "",
        f"**Research question:** {d.get('question', '')}",
        "",
        f"**Hypothesis:** {d.get('hypothesis', '')}",
        "",
        "**Why this angle earns attention:**",
        "",
        d.get("hook", ""),
        "",
        "**Why it is defensible:**",
        "",
        d.get("credibility", ""),
        "",
        "---",
        "",
        "### Contrarian Alternative",
        "",
        f"**Research question:** {c.get('question', '')}",
        "",
        f"**Hypothesis:** {c.get('hypothesis', '')}",
        "",
        "**Why this angle earns attention:**",
        "",
        c.get("hook", ""),
        "",
        "**Why it is defensible:**",
        "",
        c.get("credibility", ""),
        "",
        "---",
        "",
        "## 2. Survey Questionnaire",
        "",
        "_Designed to surface 1–2 original, quotable statistics. Estimated completion time: under 8 minutes._",
        "",
    ]

    for q in survey.get("questions", []):
        num = q.get("number", "?")
        qtype = q.get("type", "")
        question = q.get("question", "")
        options = q.get("options", [])
        purpose = q.get("purpose", "")

        lines.append(f"**Q{num}.** {question}")
        lines.append(f"*Type: {qtype} · Purpose: {purpose}*")
        if options:
            for opt in options:
                lines.append(f"- {opt}")
        lines.append("")

    lines += [
        "---",
        "",
        "## 3. Report Outline",
        "",
        outline,
        "",
        "---",
        "",
        "## 4. Contributor Invitations",
        "",
    ]

    if not invites:
        lines.append(
            "_No contributors provided. Re-run with `--contributors path/to/contributors.csv` "
            "or omit that flag to be prompted interactively._"
        )
        lines.append("")
    else:
        for item in invites:
            contrib = item["contributor"]
            invite_text = item["invite"]
            name = contrib.get("name", "Contributor")
            title = contrib.get("title", "")
            company = contrib.get("company", "")

            header_parts = [name]
            if title:
                header_parts.append(title)
            if company:
                header_parts.append(company)

            lines.append(f"### {' · '.join(header_parts)}")
            lines.append("")
            lines.append(invite_text)
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Utilities
# ─────────────────────────────────────────────────────────────────────────────

def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text[:60].lower()).strip("-")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate the front end of a peer research report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python research_engine/research.py --input research_engine/samples/brief_input.md
  python research_engine/research.py --input research_engine/samples/brief_input.md \\
      --contributors research_engine/samples/contributors.csv
""",
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the brief input markdown file (see samples/brief_input.md for format).",
    )
    parser.add_argument(
        "--contributors",
        default=None,
        help=(
            "Path to a CSV file with columns: name, role, company, public_url. "
            "If omitted, the tool prompts interactively."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
