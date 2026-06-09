#!/usr/bin/env python3
"""
pipeline_engine/pipeline.py

Turn an engagement CSV into a prioritized, personalized warm-outreach list,
and attribute each lead to the content that surfaced them.

Usage:
    python pipeline_engine/pipeline.py \
        --icp pipeline_engine/samples/icp.md \
        --engagements pipeline_engine/samples/engagements.csv \
        --sender "Jane Smith, Head of Content at Acme"
"""

import argparse
import csv
import html as _html
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

# Allow running from the repo root or from inside pipeline_engine/
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.llm import query_json, query_text
from shared.fetch import fetch
from shared.antislop import clean
from shared.report import render, Section
from shared.scoring import score_fit_batch
from shared.adapters.enrichment import enrich_contacts


# ── Warmth scoring config ──────────────────────────────────────────────────────
# Edit these module-level dicts to tune warmth without touching anything else.

ENGAGEMENT_WEIGHTS: dict[str, float] = {
    "replied":    5.0,
    "commented":  4.0,
    "downloaded": 3.0,
    "attended":   3.0,
    "shared":     3.0,
    "liked":      1.0,
}

RECENCY_DAYS = {"hot": 14, "warm": 45}  # days since engagement

WARMTH_THRESHOLDS = {"hot": 4.5, "warm": 2.0}  # weighted score cutoffs

WARMTH_RANK = {"hot": 3, "warm": 2, "cool": 1}


def score_warmth(engagement_type: str, engagement_date_str: str) -> tuple[str, float]:
    """
    Return (tier, score) for one engagement record.
    Tier is 'hot', 'warm', or 'cool'. All cutoffs are in the dicts above.
    """
    base = ENGAGEMENT_WEIGHTS.get(engagement_type.lower().strip(), 1.0)

    try:
        eng_date = date.fromisoformat(engagement_date_str.strip())
    except (ValueError, AttributeError):
        return "cool", round(base * 0.5, 2)

    days_ago = (date.today() - eng_date).days

    if days_ago <= RECENCY_DAYS["hot"]:
        recency_mult = 1.5
    elif days_ago <= RECENCY_DAYS["warm"]:
        recency_mult = 1.0
    else:
        recency_mult = 0.5

    score = base * recency_mult

    if score >= WARMTH_THRESHOLDS["hot"]:
        tier = "hot"
    elif score >= WARMTH_THRESHOLDS["warm"]:
        tier = "warm"
    else:
        tier = "cool"

    return tier, round(score, 2)


# ── Stage 1: Ingest ────────────────────────────────────────────────────────────

def ingest(csv_path: str) -> list[dict]:
    print(f"\n[1/6] Ingesting: {csv_path}")

    required = {"name", "company", "engagement_type", "engagement_date", "content_source"}
    path = Path(csv_path)
    if not path.exists():
        sys.exit(f"Error: file not found: {csv_path}")

    leads = []
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            sys.exit("Error: CSV appears to be empty.")

        cols = {c.strip().lower() for c in reader.fieldnames}
        missing = required - cols
        if missing:
            sys.exit(f"Error: CSV missing required columns: {', '.join(sorted(missing))}")

        for i, row in enumerate(reader, start=2):
            lead = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items()}
            if not lead.get("name") or not lead.get("company"):
                print(f"  [skip] Row {i}: missing name or company.")
                continue
            leads.append(lead)

    print(f"  {len(leads)} contacts loaded.")
    return leads


# ── Stage 2: Enrich ───────────────────────────────────────────────────────────

def enrich(leads: list[dict]) -> list[dict]:
    print(f"\n[2/6] Enriching {len(leads)} leads from public URLs...")

    for lead in leads:
        url = lead.get("public_url", "").strip()
        if not url:
            lead["_page_snippet"] = ""
            continue

        result = fetch(url)
        if result.ok and result.text:
            lead["_page_snippet"] = result.text[:800]
            print(f"  OK   {lead['name']:<28} {url}")
        else:
            lead["_page_snippet"] = ""
            msg = result.error or "empty page"
            print(f"  MISS {lead['name']:<28} {msg}")

    leads = enrich_contacts(leads)
    return leads


# ── Stage 3: Fit scoring ───────────────────────────────────────────────────────

def score_fit(leads: list[dict], icp_text: str) -> list[dict]:
    print(f"\n[3/6] Scoring {len(leads)} leads against ICP (single batched call)...")
    # Delegate to shared/scoring.py — same implementation used by prospecting_engine.
    scored = score_fit_batch(leads, icp_text)
    for lead in scored:
        lead.setdefault("outreach_message", "")
        if lead["disqualified"]:
            status = f"DISQUALIFIED  ({lead['disqualify_reason']})"
        else:
            status = f"fit={lead['fit_score']}/10  {lead['fit_reason']}"
        print(f"  {lead.get('name', ''):<28} {status}")
    return scored


# ── Stage 4: Warmth scoring ───────────────────────────────────────────────────

def score_warmth_all(leads: list[dict]) -> list[dict]:
    print(f"\n[4/6] Scoring warmth signals...")

    for lead in leads:
        tier, score = score_warmth(
            lead.get("engagement_type", "liked"),
            lead.get("engagement_date", ""),
        )
        lead["warmth_tier"] = tier
        lead["warmth_score"] = score
        print(
            f"  {lead['name']:<28} {tier:<5}  "
            f"({lead.get('engagement_type','?')}, {lead.get('engagement_date','?')})"
        )

    return leads


# ── Stage 5: Draft outreach ───────────────────────────────────────────────────

def draft_outreach(leads: list[dict], sender: str) -> list[dict]:
    top = [
        l for l in leads
        if not l.get("disqualified")
        and l.get("fit_score", 0) >= 7
        and l.get("warmth_tier") in ("hot", "warm")
    ]

    if not top:
        print(f"\n[5/6] No top-tier leads (need fit >= 7 + hot/warm). Skipping outreach drafts.")
        return leads

    print(f"\n[5/6] Drafting outreach for {len(top)} top-tier leads...")

    contacts = [
        {
            "name": l.get("name", ""),
            "title": l.get("title", ""),
            "company": l.get("company", ""),
            "engagement_type": l.get("engagement_type", ""),
            "content_source": l.get("content_source", ""),
            "page_snippet": (l.get("_page_snippet") or "")[:200],
        }
        for l in top
    ]

    prompt = (
        f"Write warm outreach messages on behalf of: {sender}\n\n"
        "Rules for each message:\n"
        "- 3 to 4 sentences maximum\n"
        "- Reference the specific content they engaged with\n"
        "- If page_snippet has a concrete detail, mention it; otherwise skip it\n"
        "- Open a genuine conversation, do not pitch a product\n"
        "- Sign off with the sender's first name\n"
        "- Plain text only, no markdown, no em dashes\n\n"
        f"Contacts:\n{json.dumps(contacts, indent=2)}\n\n"
        'Return a JSON array, one object per contact in the same order: '
        '{"name": "...", "company": "...", "message": "..."}'
    )

    results = query_json(prompt)

    draft_map: dict[tuple[str, str], str] = {}
    if isinstance(results, list):
        for r in results:
            if isinstance(r, dict):
                key = (r.get("name", ""), r.get("company", ""))
                draft_map[key] = r.get("message", "")

    for lead in leads:
        key = (lead.get("name", ""), lead.get("company", ""))
        raw = draft_map.get(key, "")
        if raw:
            lead["outreach_message"] = clean(raw)
            print(f"  Drafted: {lead['name']} ({lead['company']})")

    return leads


# ── Rank ──────────────────────────────────────────────────────────────────────

def rank(leads: list[dict]) -> list[dict]:
    def sort_key(lead: dict):
        disq = 1 if lead.get("disqualified") else 0
        fit = -(lead.get("fit_score", 0))
        warmth = -(WARMTH_RANK.get(lead.get("warmth_tier", "cool"), 0))
        return (disq, fit, warmth)

    return sorted(leads, key=sort_key)


# ── Stage 6: Attribution ──────────────────────────────────────────────────────

def attribute(leads: list[dict]) -> list[dict]:
    """Return content attribution sorted by qualified warm lead count."""
    print(f"\n[6/6] Content attribution (qualified = not disqualified, fit >= 6, hot/warm)...")

    content_map: dict[str, list[str]] = defaultdict(list)
    for lead in leads:
        if lead.get("disqualified"):
            continue
        if lead.get("fit_score", 0) < 6:
            continue
        if lead.get("warmth_tier") not in ("hot", "warm"):
            continue
        content = lead.get("content_source") or "unknown"
        content_map[content].append(f"{lead['name']} ({lead['company']})")

    summary = sorted(
        [{"content": k, "count": len(v), "leads": v} for k, v in content_map.items()],
        key=lambda x: -x["count"],
    )

    for row in summary:
        print(f"  {row['count']:2}x  {row['content']}")

    return summary


# ── Output writers ────────────────────────────────────────────────────────────

_CSV_FIELDS = [
    "name", "title", "company", "company_size",
    "fit_score", "fit_reason", "disqualified", "disqualify_reason",
    "warmth_tier", "warmth_score",
    "engagement_type", "engagement_date", "content_source",
    "public_url", "outreach_message",
]


def write_csv(leads: list[dict], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(leads)
    print(f"  CSV      -> {path}")


def write_markdown(leads: list[dict], attribution: list[dict], path: Path) -> None:
    qualified = [l for l in leads if not l.get("disqualified")]
    disq = [l for l in leads if l.get("disqualified")]

    lines = ["# Pipeline Engine: Lead List\n", "## Prioritized Leads\n"]
    lines.append("| # | Name | Company | Fit | Warmth | Source Content | Outreach snippet |")
    lines.append("|---|------|---------|-----|--------|----------------|-----------------|")

    for i, lead in enumerate(qualified, 1):
        msg = (lead.get("outreach_message") or "")
        snippet = (msg[:55] + "...") if len(msg) > 55 else msg
        snippet = snippet.replace("|", "/")
        lines.append(
            f"| {i} | **{lead.get('name','')}** | {lead.get('company','')} "
            f"| {lead.get('fit_score','')}/10 | {lead.get('warmth_tier','')} "
            f"| {lead.get('content_source','')} | {snippet} |"
        )

    if disq:
        lines.append(f"\n### Disqualified ({len(disq)})\n")
        for l in disq:
            lines.append(f"- **{l.get('name')}** ({l.get('company')}) — {l.get('disqualify_reason','')}")

    lines.append("\n## Content Attribution\n")
    lines.append("| Content | Warm Qualified Leads | Who |")
    lines.append("|---------|---------------------|-----|")
    for row in attribution:
        lines.append(f"| {row['content']} | {row['count']} | {', '.join(row['leads'])} |")

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Markdown -> {path}")


def write_html(
    leads: list[dict],
    attribution: list[dict],
    path: Path,
    sender: str,
    icp_path: str,
) -> None:
    e = _html.escape

    qualified = [l for l in leads if not l.get("disqualified")]
    disq = [l for l in leads if l.get("disqualified")]

    # Warmth badge CSS classes already defined in shared/report.py
    warmth_class = {"hot": "tag-hot", "warm": "tag-warm", "cool": "tag-cool"}

    # ── Lead table
    rows_html = []
    for i, lead in enumerate(qualified, 1):
        tier = lead.get("warmth_tier", "cool")
        msg = lead.get("outreach_message", "")
        if msg:
            msg_html = (
                f'<details><summary style="cursor:pointer;color:#2a6dd9;font-size:.85rem">View draft</summary>'
                f'<p style="white-space:pre-wrap;font-size:.85rem;color:#444;margin-top:.5rem">{e(msg)}</p></details>'
            )
        else:
            msg_html = '<span style="color:#ccc">—</span>'

        rows_html.append(f"""  <tr>
    <td style="text-align:center;color:#888">{i}</td>
    <td><strong>{e(lead.get('name',''))}</strong><br>
        <small style="color:#666">{e(lead.get('title',''))}</small></td>
    <td>{e(lead.get('company',''))}<br>
        <small style="color:#888">{e(str(lead.get('company_size','')))}</small></td>
    <td style="text-align:center">
        <strong style="font-size:1.1rem">{e(str(lead.get('fit_score','')))}/10</strong><br>
        <small style="color:#666">{e(lead.get('fit_reason',''))}</small></td>
    <td style="text-align:center"><span class="tag {warmth_class.get(tier,'tag-cool')}">{e(tier)}</span></td>
    <td><small>{e(lead.get('content_source',''))}</small><br>
        <small style="color:#888">{e(lead.get('engagement_type',''))}</small></td>
    <td>{msg_html}</td>
  </tr>""")

    table_html = (
        "<table>\n"
        "  <thead><tr>"
        "<th>#</th><th>Name</th><th>Company</th>"
        "<th>Fit</th><th>Warmth</th><th>Source Content</th><th>Outreach Draft</th>"
        "</tr></thead>\n"
        "  <tbody>\n" + "\n".join(rows_html) + "\n  </tbody>\n</table>"
    )

    disq_html = ""
    if disq:
        items = "".join(
            f"<li><strong>{e(l.get('name',''))}</strong> ({e(l.get('company',''))}) "
            f"&mdash; {e(l.get('disqualify_reason',''))}</li>"
            for l in disq
        )
        disq_html = (
            f'<p style="margin-top:1.5rem;color:#888;font-size:.9rem">'
            f'{len(disq)} contacts disqualified against ICP:</p>'
            f'<ul style="color:#888;font-size:.9rem">{items}</ul>'
        )

    # ── Attribution table
    total = sum(r["count"] for r in attribution) or 1
    attr_rows = []
    for row in attribution:
        pct = round(row["count"] / total * 100)
        bar = (
            f'<div style="background:#e8e8e4;border-radius:4px;height:8px;width:100%">'
            f'<div style="background:#1a1a2e;border-radius:4px;height:8px;width:{pct}%"></div>'
            f'</div>'
        )
        attr_rows.append(
            f"  <tr>"
            f"<td>{e(row['content'])}</td>"
            f"<td style='text-align:center'><strong>{row['count']}</strong></td>"
            f"<td style='width:120px'>{bar}</td>"
            f"<td style='font-size:.85rem;color:#666'>{e(', '.join(row['leads']))}</td>"
            f"</tr>"
        )

    attr_html = (
        "<table>\n"
        "  <thead><tr><th>Content / Query</th><th>Warm Leads</th><th></th><th>Contacts</th></tr></thead>\n"
        "  <tbody>\n" + "\n".join(attr_rows) + "\n  </tbody>\n</table>"
    )

    # ── Summary box
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    drafted = sum(1 for l in leads if l.get("outreach_message"))
    meta_html = (
        f"<p>"
        f"<strong>Sender:</strong> {e(sender)}<br>"
        f"<strong>ICP file:</strong> {e(icp_path)}<br>"
        f"<strong>Run at:</strong> {now}<br>"
        f"<strong>Contacts ingested:</strong> {len(leads)}<br>"
        f"<strong>Qualified (not disqualified):</strong> {len(qualified)}<br>"
        f"<strong>Outreach drafted (fit &ge; 7, hot/warm):</strong> {drafted}"
        f"</p>"
    )

    sections = [
        Section("Summary", meta_html),
        Section("Prioritized Lead List", table_html + disq_html),
        Section("Content Attribution", attr_html),
    ]

    html_out = render(
        title="Pipeline Engine: Warm Outreach Dashboard",
        subtitle=f"Run {now}",
        sections=sections,
    )

    path.write_text(html_out, encoding="utf-8")
    print(f"  HTML     -> {path}")


# ── CLI entry point ───────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Turn an engagement CSV into a prioritized warm-outreach list.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            '  python pipeline_engine/pipeline.py \\\n'
            '    --icp pipeline_engine/samples/icp.md \\\n'
            '    --engagements pipeline_engine/samples/engagements.csv \\\n'
            '    --sender "Jane Smith, Head of Content at Acme"'
        ),
    )
    parser.add_argument("--icp", required=True, help="ICP definition file (markdown or plain text)")
    parser.add_argument("--engagements", required=True, help="Engagement CSV file")
    parser.add_argument(
        "--sender",
        required=True,
        help='Sender identity for outreach, e.g. "Jane Smith, Head of Content at Acme"',
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Parent directory for output files (default: outputs/)",
    )
    args = parser.parse_args()

    icp_path = Path(args.icp)
    if not icp_path.exists():
        sys.exit(f"Error: ICP file not found: {args.icp}")
    icp_text = icp_path.read_text(encoding="utf-8")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path(args.output_dir) / f"pipeline_{ts}"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*62}")
    print(f"  Pipeline Engine")
    print(f"  ICP:         {args.icp}")
    print(f"  Engagements: {args.engagements}")
    print(f"  Sender:      {args.sender}")
    print(f"  Output:      {out_dir}/")
    print(f"{'='*62}")

    leads = ingest(args.engagements)
    leads = enrich(leads)
    leads = score_fit(leads, icp_text)
    leads = score_warmth_all(leads)
    leads = rank(leads)
    leads = draft_outreach(leads, args.sender)
    attribution = attribute(leads)

    print(f"\n[Output] Writing to {out_dir}/")
    write_csv(leads, out_dir / "leads.csv")
    write_markdown(leads, attribution, out_dir / "leads.md")
    write_html(leads, attribution, out_dir / "report.html", args.sender, args.icp)

    print(f"\n{'='*62}")
    print(f"  Done.")
    print(f"  Open: {out_dir}/report.html")
    print(f"{'='*62}\n")


if __name__ == "__main__":
    main()
