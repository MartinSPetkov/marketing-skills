#!/usr/bin/env python3
"""
AEO content brief generator.

Turns a single buyer-intent query into:
  - A markdown content brief optimised for AI engine citation
  - A valid JSON-LD schema file ready to paste into the page head

Usage:
    python brief.py --query "best contract testing tools" \\
                    --context samples/context.md \\
                    --urls samples/urls.txt

Outputs are written to: outputs/<query-slug>/brief.md and schema.jsonld
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

# Allow running from brief_generator/ directly or from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.adapters.engines import query_engines
from shared.antislop import clean
from shared.fetch import fetch
from shared.llm import query_json, query_text


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate an AEO content brief + JSON-LD schema markup.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--query", required=True,
        help='Buyer-intent query, e.g. "best contract testing tools"',
    )
    p.add_argument(
        "--context", required=True,
        help="Path to company context file (.md or .txt). See samples/context.md.",
    )
    p.add_argument(
        "--urls", default=None,
        help="Optional path to a file listing competitor/reference URLs, one per line.",
    )
    p.add_argument(
        "--schema",
        choices=["auto", "faqpage", "article", "howto", "definedterm"],
        default="auto",
        help=(
            "JSON-LD schema type. 'auto' picks from the recommended page type. "
            "Override when your CMS template requires a specific schema."
        ),
    )
    return p.parse_args()


# ── Utilities ─────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def load_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        sys.exit(f"[error] File not found: {path}")
    return p.read_text(encoding="utf-8").strip()


def load_urls(path: str) -> list[str]:
    raw = load_file(path)
    return [
        line.strip()
        for line in raw.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def _trim(text: str, chars: int = 2500) -> str:
    if len(text) <= chars:
        return text
    return text[:chars] + "\n[truncated for context]"


def _extract_company_name(context: str) -> str:
    for line in context.strip().splitlines():
        stripped = line.strip().lstrip("# ").strip()
        if stripped:
            return stripped
    return "Company"


# ── Stage 1: Recon ────────────────────────────────────────────────────────────

def run_recon(query: str, urls: list[str]) -> dict:
    """Fetch reference URLs and ask Claude what it currently surfaces for the query."""

    fetched: list[dict] = []
    for url in urls:
        print(f"    Fetching {url} ...")
        result = fetch(url)
        if not result.ok:
            print(f"    [warn] Skipped {url}: {result.error}")
            continue
        fetched.append({
            "url": url,
            "headings": result.headings[:30],
            "faq": result.faq[:10],
            "body_excerpt": _trim(result.body, 1800),
            "existing_jsonld_types": [s.get("@type") for s in result.jsonld if s.get("@type")],
        })

    # Ask Claude what it currently surfaces for this query — captures the
    # baseline before we try to improve on it.
    print("    Querying Claude for current AI-engine coverage...")
    engine_prompt = (
        f'Answer this buyer query as you would in a live conversation:\n"{query}"\n\n'
        "After your answer, output a JSON block with these keys:\n"
        '- "top_claims": list of the 5 strongest claims you just made\n'
        '- "entities": list of specific tools, companies, standards, or products you named\n'
        '- "unanswered_subquestions": list of 4 sub-questions a buyer would still have\n'
        '- "stats_cited": list of any figures or statistics you mentioned (empty list if none)\n'
        "\nFormat: answer text first, then the JSON block on its own line."
    )
    raw_response = query_engines(engine_prompt, engines=["claude"]).get("claude") or ""

    # Parse the trailing JSON block
    ai_structured: dict = {
        "answer": raw_response,
        "top_claims": [],
        "entities": [],
        "unanswered_subquestions": [],
        "stats_cited": [],
    }
    json_match = re.search(r"\{[\s\S]*\}", raw_response)
    if json_match:
        try:
            parsed = json.loads(json_match.group())
            if isinstance(parsed, dict):
                ai_structured.update(parsed)
                # Keep the full answer text too
                ai_structured["answer"] = raw_response
        except json.JSONDecodeError:
            pass

    return {"fetched_urls": fetched, "ai_coverage": ai_structured}


# ── Stage 2: Gap analysis ────────────────────────────────────────────────────

def run_gap_analysis(query: str, context: str, recon: dict) -> dict:
    """Compare existing coverage against the company's angle; surface the gaps."""

    # Build a compact competitor summary
    competitor_block = ""
    for item in recon["fetched_urls"]:
        headings_text = "\n".join(
            f"  H{h['level']}: {h['text']}" for h in item["headings"][:15]
        )
        faq_text = "\n".join(f"  Q: {f['question']}" for f in item["faq"][:8])
        competitor_block += (
            f"\nURL: {item['url']}\n"
            f"Headings:\n{headings_text}\n"
            f"FAQs:\n{faq_text}\n"
            f"Excerpt:\n{_trim(item['body_excerpt'], 600)}\n---\n"
        )

    if not competitor_block:
        competitor_block = "(No reference URLs provided. Gap analysis uses AI coverage only.)"

    ai_block = (
        f"Entities named: {recon['ai_coverage'].get('entities', [])}\n"
        f"Top claims: {recon['ai_coverage'].get('top_claims', [])}\n"
        f"Sub-questions left unanswered: {recon['ai_coverage'].get('unanswered_subquestions', [])}\n"
        f"Stats cited: {recon['ai_coverage'].get('stats_cited', [])}"
    )

    prompt = (
        "You are an AEO (Answer Engine Optimisation) strategist.\n\n"
        f'TARGET QUERY: "{query}"\n\n'
        f"COMPANY CONTEXT:\n{context}\n\n"
        f"WHAT AI ENGINES CURRENTLY SURFACE FOR THIS QUERY:\n{_trim(ai_block, 1500)}\n\n"
        f"COMPETITOR / REFERENCE PAGE COVERAGE:\n{_trim(competitor_block, 2500)}\n\n"
        "Identify the gaps this company can own.\n\n"
        "Return JSON with these keys:\n"
        '- "unanswered_subquestions": list of 5 sub-questions no existing page answers clearly\n'
        '- "missing_definitions": list of 2-3 terms or concepts not defined anywhere\n'
        '- "unique_angle": the specific claim or perspective this company can own (1-2 sentences)\n'
        '- "recommended_page_type": one of "faq", "comparison", "definition", "guide"\n'
        '- "intent_label": one of "informational", "commercial", "navigational"\n'
        '- "why_page_type": one sentence explaining the page type recommendation'
    )

    result = query_json(prompt)
    return result if isinstance(result, dict) else {}


# ── Stage 3: Brief assembly ──────────────────────────────────────────────────

def assemble_brief(query: str, context: str, recon: dict, gaps: dict) -> dict:
    """Ask Claude to produce the full structured brief."""

    ai_cov = recon["ai_coverage"]

    prompt = (
        "You are writing an AEO content brief. The goal: produce a page that "
        "ChatGPT, Claude, Perplexity, and Gemini will cite as the authoritative "
        "answer to the target query. AI engines cite pages that are answer-first, "
        "well-structured, entity-rich, and marked up with schema.org JSON-LD.\n\n"
        f'TARGET QUERY: "{query}"\n\n'
        f"COMPANY CONTEXT:\n{context}\n\n"
        f"GAP ANALYSIS:\n{json.dumps(gaps, indent=2)}\n\n"
        f"AI ENGINE CURRENTLY NAMES: {ai_cov.get('entities', [])}\n"
        f"AI ENGINE'S TOP CLAIMS: {ai_cov.get('top_claims', [])}\n"
        f"SUB-QUESTIONS AI LEAVES OPEN: {ai_cov.get('unanswered_subquestions', [])}\n\n"
        "Produce a complete content brief. Return JSON with these exact keys:\n\n"
        '- "target_query": the query as provided\n'
        '- "search_intent": "informational", "commercial", or "navigational"\n'
        '- "recommended_page_type": "faq", "comparison", "definition", or "guide"\n'
        '- "answer_summary": 2-3 sentences an AI engine can lift verbatim as a direct '
        "answer. Answer-first, factual, specific. No hedging, no em dashes, no filler openers.\n"
        '- "outline": list of objects with "level" (2 or 3), "heading" (text), '
        '"purpose" (one-sentence writer note)\n'
        '- "faqs": list of 6-8 objects with "question" and "answer" (1-3 direct, '
        "factual sentences each; no em dashes; no hollow openers)\n"
        '- "stats_and_claims": list of objects with "claim" and "source_placeholder" '
        '(write "[SOURCE NEEDED: type of source]" for anything the writer must verify)\n'
        '- "named_entities": list of specific tools, companies, standards, or concepts to mention\n'
        '- "internal_link_suggestions": list of objects with "anchor_text" and '
        '"target_page_description"\n'
        '- "external_link_suggestions": list of objects with "anchor_text" and '
        '"target_description" (describe what to link to; do not invent specific URLs)\n'
        '- "credibility_signals": list of 4-5 specific signals to add '
        "(author bio format, data citations, expert quotes, third-party validation, etc.)"
    )

    result = query_json(prompt)
    return result if isinstance(result, dict) else {}


def format_brief(data: dict, query: str = "") -> str:
    """Convert the structured brief into a clean markdown document.

    Passes the answer_summary through antislop for a hard prose gate.
    FAQ answers are written by the same LLM under strict style instructions
    and are not re-run through antislop to keep the pipeline fast.
    """

    # Hard prose gate on the most-cited block
    raw_summary = data.get("answer_summary", "")
    answer_summary = clean(raw_summary) if raw_summary else ""

    today = date.today().isoformat()
    target_query = data.get("target_query") or query
    page_type = (data.get("recommended_page_type") or "").title()
    intent = (data.get("search_intent") or "").title()

    lines: list[str] = [
        f"# Content Brief: {target_query}",
        f"\n_Generated: {today}_\n",
        "---\n",
        "## Target Query",
        f"`{target_query}`\n",
        "## Search Intent",
        f"{intent}\n",
        "## Recommended Page Type",
        f"{page_type}\n",
        "## Answer-First Summary",
        "_Place this block in the first 100 words. AI engines can cite it verbatim._\n",
        f"> {answer_summary}\n",
        "## Page Outline",
    ]

    for item in data.get("outline", []):
        level = item.get("level", 2)
        heading = item.get("heading", "")
        purpose = item.get("purpose", "")
        prefix = "##" if level == 2 else "###"
        lines.append(f"{prefix} {heading}")
        if purpose:
            lines.append(f"_{purpose}_\n")

    lines += [
        "\n## FAQ Block",
        "_Mark up with FAQPage JSON-LD. See schema.jsonld._\n",
    ]
    for faq in data.get("faqs", []):
        q = faq.get("question", "")
        a = faq.get("answer", "")
        lines.append(f"**Q: {q}**")
        lines.append(f"{a}\n")

    lines += [
        "## Statistics and Claims to Include",
        "_Replace every [SOURCE NEEDED] placeholder with a real citation before publishing._\n",
    ]
    for item in data.get("stats_and_claims", []):
        claim = item.get("claim", "")
        placeholder = item.get("source_placeholder", "")
        lines.append(f"- {claim}")
        if placeholder:
            lines.append(f"  _{placeholder}_")

    lines += ["\n## Named Entities to Mention",
              "_Include these by name. AI engines use entity co-occurrence as a relevance signal._\n"]
    for entity in data.get("named_entities", []):
        lines.append(f"- {entity}")

    lines += ["\n## Internal Link Suggestions"]
    for link in data.get("internal_link_suggestions", []):
        anchor = link.get("anchor_text", "")
        target = link.get("target_page_description", "")
        lines.append(f"- **{anchor}** → {target}")

    lines += ["\n## External Link Suggestions"]
    for link in data.get("external_link_suggestions", []):
        anchor = link.get("anchor_text", "")
        target = link.get("target_description", "")
        lines.append(f"- **{anchor}** → {target}")

    lines += ["\n## Credibility Signals to Add"]
    for signal in data.get("credibility_signals", []):
        lines.append(f"- {signal}")

    return "\n".join(lines) + "\n"


# ── Stage 4: Schema generation ───────────────────────────────────────────────

_PAGE_TYPE_TO_SCHEMA = {
    "faq": "FAQPage",
    "comparison": "Article",
    "definition": "DefinedTerm",
    "guide": "HowTo",
}

_SCHEMA_CLI_MAP = {
    "faqpage": "FAQPage",
    "article": "Article",
    "howto": "HowTo",
    "definedterm": "DefinedTerm",
}


def generate_schema(query: str, context: str, brief_data: dict, schema_override: str) -> dict:
    """Produce valid JSON-LD appropriate to the page type."""

    if schema_override != "auto":
        schema_type = _SCHEMA_CLI_MAP.get(schema_override, "Article")
    else:
        page_type = brief_data.get("recommended_page_type", "guide")
        schema_type = _PAGE_TYPE_TO_SCHEMA.get(page_type, "Article")

    faqs = brief_data.get("faqs", [])
    outline = brief_data.get("outline", [])
    answer_summary = brief_data.get("answer_summary", "")
    company_name = _extract_company_name(context)
    today = date.today().isoformat()

    if schema_type == "FAQPage":
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": faq.get("question", ""),
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq.get("answer", ""),
                    },
                }
                for faq in faqs
            ],
        }

    if schema_type == "HowTo":
        h2_steps = [item for item in outline if item.get("level") == 2]
        return {
            "@context": "https://schema.org",
            "@type": "HowTo",
            "name": query,
            "description": answer_summary,
            "step": [
                {
                    "@type": "HowToStep",
                    "name": step.get("heading", ""),
                    "text": step.get("purpose", ""),
                }
                for step in h2_steps
            ],
        }

    if schema_type == "DefinedTerm":
        return {
            "@context": "https://schema.org",
            "@type": "DefinedTerm",
            "name": query,
            "description": answer_summary,
            "inDefinedTermSet": {
                "@type": "DefinedTermSet",
                "name": f"{company_name} Glossary",
            },
        }

    # Article (default for comparison pages and fallback)
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": query,
        "description": answer_summary,
        "author": {
            "@type": "Organization",
            "name": company_name,
        },
        "datePublished": today,
        "dateModified": today,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    args = parse_args()

    print(f'\nBrief Generator — "{args.query}"')
    print("=" * 60)

    context = load_file(args.context)
    urls = load_urls(args.urls) if args.urls else []

    if urls:
        print(f"Reference URLs loaded: {len(urls)}")
    else:
        print("Reference URLs: none (running on AI coverage only)")

    slug = slugify(args.query)
    out_dir = Path(__file__).parent.parent / "outputs" / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Recon ────────────────────────────────────────────────────────────
    print("\n[1/4] Recon: fetching URLs and querying AI engine...")
    recon = run_recon(args.query, urls)
    fetched_count = len(recon["fetched_urls"])
    entities_found = recon["ai_coverage"].get("entities", [])
    if fetched_count:
        print(f"  {fetched_count} URL(s) fetched.")
    print(f"  AI engine named {len(entities_found)} entities: {entities_found[:6]}")

    # ── 2. Gap analysis ─────────────────────────────────────────────────────
    print("\n[2/4] Gap analysis: mapping coverage against company angle...")
    gaps = run_gap_analysis(args.query, context, recon)
    unanswered = gaps.get("unanswered_subquestions", [])
    page_type = gaps.get("recommended_page_type", "unknown")
    print(f"  Recommended page type: {page_type}")
    print(f"  Unanswered sub-questions found: {len(unanswered)}")
    if gaps.get("unique_angle"):
        print(f"  Unique angle: {gaps['unique_angle']}")

    # ── 3. Brief assembly ───────────────────────────────────────────────────
    print("\n[3/4] Assembling brief (anti-slop pass on answer summary)...")
    brief_data = assemble_brief(args.query, context, recon, gaps)

    # Carry over page type from gap analysis if not set
    if not brief_data.get("recommended_page_type") and page_type:
        brief_data["recommended_page_type"] = page_type

    brief_md = format_brief(brief_data, query=args.query)
    brief_path = out_dir / "brief.md"
    brief_path.write_text(brief_md, encoding="utf-8")
    faq_count = len(brief_data.get("faqs", []))
    outline_count = len(brief_data.get("outline", []))
    print(f"  {outline_count} outline sections, {faq_count} FAQ pairs.")
    print(f"  Written: {brief_path}")

    # ── 4. Schema generation ────────────────────────────────────────────────
    print("\n[4/4] Generating JSON-LD schema...")
    schema = generate_schema(args.query, context, brief_data, args.schema)
    schema_path = out_dir / "schema.jsonld"
    schema_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Schema type: {schema.get('@type')}")
    print(f"  Written: {schema_path}")

    # ── Done ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Done.\n")
    print(f"  Brief:   {brief_path}")
    print(f"  Schema:  {schema_path}")
    print("\n  Validate schema: https://search.google.com/test/rich-results")


if __name__ == "__main__":
    main()
