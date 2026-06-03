# research_engine

Turns a research theme into the front end of a peer research report: an insight angle,
a survey questionnaire, a report outline, and personalized contributor invitations.

**Why this asset works:** peer research reports get B2B companies into rooms with accounts
that will not take a cold call. The ask is "contribute to a report your peers will read"
rather than "take a sales call." This tool engineers that asset from the strategy layer
down to the outreach copy.

---

## Run command

```bash
# Minimal — contributors entered interactively
python research_engine/research.py --input research_engine/samples/brief_input.md

# With a contributors CSV
python research_engine/research.py \
    --input research_engine/samples/brief_input.md \
    --contributors research_engine/samples/contributors.csv
```

Run from the repo root. Authenticate first:

```bash
claude login       # choose Claude.ai, log in with your Pro or Max plan
claude /status     # confirm the subscription is the active auth method
unset ANTHROPIC_API_KEY
```

---

## Inputs

### Brief input file (`--input`)

A markdown file with these sections (see `samples/brief_input.md`):

| Section | Required | Content |
|---|---|---|
| `## Category and theme` | Yes | The research topic and what you want to find out |
| `## Company running the research` | Yes | Your company, positioning, and why you own this space |
| `## ICP` | No | Who the target respondents are |
| `## Reference URLs (optional)` | No | Public articles or reports to ground the angle — one URL per line |

### Contributors file (`--contributors`)

A CSV with columns: `name`, `role`, `company`, `public_url`, `notes`.

If `--contributors` is omitted, the tool prompts for contributor info interactively.
Each contributor needs at minimum a name and company. The `public_url` is used to
fetch public page content for personalization context.

---

## What the tool produces

A single markdown file at `outputs/research_engine/<slug>/report_package.md` with four sections:

1. **Insight angle** — a defensible angle (the most credible, evidence-grounded take) plus
   a contrarian alternative (the bolder counter-narrative). Both include a research question,
   a falsifiable hypothesis, and a hook for why practitioners will care.

2. **Survey questionnaire** — 8–12 questions engineered to surface one or two original,
   quotable statistics. Mix of context questions (to segment results), quantitative questions
   (to produce headline stats), open-ended questions (to produce quotes), and a contrarian
   test question.

3. **Report outline** — a structured section-by-section outline showing where survey data
   and contributor quotes slot in. Marked with `[SURVEY DATA: ...]` and `[CONTRIBUTOR QUOTE: ...]`
   placeholders. Includes Methodology and Contributors sections.

4. **Contributor invitations** — one short, personalized email per contributor, framed as
   a peer research ask, not a sales ask. Each invite references something specific about the
   person or their company. All invitation prose passes through the anti-slop gate.

---

## Honest limits

**Contact finding is not included.** This tool works on whatever public info you paste in.
It does not find email addresses, verify roles, or search LinkedIn.

Real contact enrichment requires a paid tool. The adapter is already wired up in
`shared/adapters/enrichment.py` — set one environment variable to activate it:

| Tool | What to set |
|---|---|
| Clay | `ENRICHMENT_SOURCE=clay` + `CLAY_API_KEY=...` |
| Apollo | `ENRICHMENT_SOURCE=apollo` + `APOLLO_API_KEY=...` |
| CRM CSV export | `ENRICHMENT_SOURCE=csv` + `CRM_EXPORT_PATH=path/to/export.csv` |

Until you set one of these, the tool runs on the manual data you provide and logs a
single notice saying so. It never pretends enrichment ran when it did not.

**LinkedIn URLs are blocked by design.** `shared/fetch.py` will not fetch LinkedIn pages.
If a contributor URL is a LinkedIn profile, the tool skips the fetch and generates the
invite from the info you provided.

---

## Sample output structure

```
outputs/
└── research_engine/
    └── the-state-of-ai-search-visibility-for-b2b-saa/
        └── report_package.md
```

The output file is self-contained markdown — paste it into Notion, Docs, or any editor.
