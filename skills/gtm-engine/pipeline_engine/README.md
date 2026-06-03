# pipeline_engine

Turn a list of engaged contacts into a prioritized, personalized warm-outreach list. Attribute each lead to the content that surfaced them.

## Run

```bash
python pipeline_engine/pipeline.py \
  --icp pipeline_engine/samples/icp.md \
  --engagements pipeline_engine/samples/engagements.csv \
  --sender "Your Name, Your Title at Your Company"
```

Output lands in `outputs/pipeline_TIMESTAMP/`:

| File | Contents |
|------|----------|
| `report.html` | Self-contained HTML dashboard — open in any browser, no server needed |
| `leads.csv` | Full ranked lead list with all scores and outreach drafts |
| `leads.md` | Markdown table view |

## What it does

```
Engagement CSV  →  Ingest  →  Enrich  →  Fit score  →  Warmth score
                                                              ↓
HTML dashboard  ←  Attribute  ←  Draft outreach  ←  Rank  ←┘
```

Six stages, each printed to the console as it runs:

1. **Ingest** — validates the CSV, reports skipped rows
2. **Enrich** — fetches each contact's public URL via `shared/fetch.py`; runs the enrichment adapter (manual default; Clay/Apollo/CRM optional)
3. **Fit score** — one batched Claude call scores all leads 1-10 against your ICP; clear mismatches are flagged as disqualified
4. **Warmth score** — pure Python: engagement type × recency → hot / warm / cool
5. **Draft outreach** — one batched Claude call drafts personalized messages for top-tier leads (fit ≥ 7 + hot or warm), passed through `shared/antislop.py`
6. **Attribute** — which content produced the most qualified warm leads

## Inputs

### ICP file (`--icp`)

Plain text or markdown. Include: target roles, company size, industry, and disqualifiers. See `samples/icp.md`.

### Engagement CSV (`--engagements`)

Required columns:

| Column | Description |
|--------|-------------|
| `name` | Contact's full name |
| `title` | Job title |
| `company` | Company name |
| `company_size` | Approximate headcount |
| `public_url` | Public URL about this contact or company (about page, blog, etc.) |
| `engagement_type` | `liked` / `commented` / `downloaded` / `attended` / `shared` / `replied` |
| `engagement_date` | ISO date: `YYYY-MM-DD` |
| `content_source` | Which content piece or query surfaced them |

Export this from your CRM, LinkedIn analytics export, or content platform. The tool reads a file you provide; it does not scrape LinkedIn or connect to any CRM directly.

### Sender (`--sender`)

A string identifying who is sending the outreach, used to sign the draft messages.

```bash
--sender "Maya Chen, Head of Content at Stormlight"
```

## Warmth tiers

Warmth is computed from two inputs: engagement type and days since engagement.

| Tier | Logic |
|------|-------|
| **Hot** | Weighted score ≥ 4.5 (strong-intent action within 14 days) |
| **Warm** | Weighted score ≥ 2.0 (solid action within 45 days) |
| **Cool** | Everything else |

Engagement weights (highest to lowest): `replied` (5), `commented` (4), `downloaded / attended / shared` (3), `liked` (1).

All thresholds and weights live in module-level dicts at the top of `pipeline.py`. Tune them without touching any other code.

## Top-tier outreach cutoff

Outreach is drafted for leads that meet both conditions:

- Fit score ≥ 7 (strong ICP match)
- Warmth tier is **hot** or **warm**

Leads that meet only one condition appear in the ranked list without a draft. Disqualified leads appear at the bottom.

## Plug-in points

### Contact enrichment (Clay, Apollo, CRM)

Set environment variables to activate a paid enrichment source. The tool always runs fully on manual CSV data — no key required.

```bash
# Clay
export CLAY_API_KEY=your_key
export ENRICHMENT_SOURCE=clay

# Apollo
export APOLLO_API_KEY=your_key
export ENRICHMENT_SOURCE=apollo

# CRM export (match on name+company or email)
export ENRICHMENT_SOURCE=csv
export CRM_EXPORT_PATH=path/to/crm_export.csv
```

See `shared/adapters/enrichment.py` for implementation. Clay and Apollo stubs are there to fill in when you have keys.

### Live engagement capture

Live signal capture happens in your CRM, LinkedIn analytics, or tools like Clay and Apollo — not here. Export a CSV from those systems and pass it to `--engagements`. This is the documented boundary: the tool processes signals you provide, it does not capture them.

## Authentication

Uses your Claude Pro or Max subscription via the `claude` CLI. No API key needed.

```bash
claude login             # authenticate once
claude /status           # confirm subscription is active
unset ANTHROPIC_API_KEY  # ensure no key overrides the subscription
```

Pro plan limits are tighter than Max. A full run on a large list may need a minute between stages if you hit a rate limit — the tool will say so plainly.
