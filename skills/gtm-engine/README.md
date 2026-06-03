# GTM Engine

Five standalone Python CLI tools that map to the B2B revenue loop: get found, score signal, run warm outreach, and trace every lead back to the content that surfaced it.

Built on a Claude Pro or Max subscription. No API key, no per-token billing. Each tool runs from a single command.

---

## The five tools

| Tool | What it does | Input | Key output |
|---|---|---|---|
| [`entity_auditor`](entity_auditor/README.md) | Audits a brand's entity authority — how recognisable it is to AI engines — and generates the assets to fix it | Brand name + URL | HTML report, Organisation JSON-LD |
| [`pipeline_engine`](pipeline_engine/README.md) | Turns engaged contacts into a prioritised warm-outreach list and attributes each lead to the content that surfaced them | ICP file + engagement CSV | HTML dashboard, ranked leads CSV |
| [`brief_generator`](brief_generator/README.md) | Turns a buyer-intent query into an AEO content brief and ready-to-paste JSON-LD schema | Query + company context | Markdown brief, schema `.jsonld` |
| [`voice_engine`](voice_engine/README.md) | Turns a research finding into a 14-day LinkedIn sequence in a specific executive's voice, with a hard anti-slop gate | Post corpus + research input | 14 posts, before/after HTML |
| [`research_engine`](research_engine/README.md) | Produces the front end of an original research report: insight angle, survey, outline, and personalised contributor invites | Research brief + contributor list | Full markdown package |

The tools form a loop: `brief_generator` and `entity_auditor` get the brand found by AI engines → `voice_engine` and `research_engine` build content that produces engagement → `pipeline_engine` turns that engagement into pipeline and closes the attribution loop.

---

## Setup

**Prerequisites:** Python 3.11+, Node.js (for the Claude CLI), a Claude Pro or Max subscription.

```bash
# 1. Install the Claude CLI (one-time)
npm install -g @anthropic-ai/claude-code

# 2. Authenticate with your subscription
claude login        # choose Claude.ai, log in with your Pro or Max account

# 3. Confirm subscription is the active auth method
claude /status

# 4. Clone and install Python dependencies
git clone https://github.com/your-org/gtm-engine.git
cd gtm-engine
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 5. Critical: ensure no API key overrides your subscription
unset ANTHROPIC_API_KEY
```

Run `unset ANTHROPIC_API_KEY` in every new terminal before running the tools. If that variable is set, Claude Code bills your API account instead of your subscription.

---

## Quick-start commands

Run all commands from the repo root.

```bash
# Audit entity authority for any public B2B SaaS site
python entity_auditor/entity_audit.py --brand "Acme" --url "https://acme.com"

# Score and prioritise an engagement list
python pipeline_engine/pipeline.py \
  --icp pipeline_engine/samples/icp.md \
  --engagements pipeline_engine/samples/engagements.csv \
  --sender "Your Name, Your Title"

# Generate an AEO content brief
python brief_generator/brief.py \
  --query "best contract testing tools" \
  --context brief_generator/samples/context.md

# Generate a 14-day LinkedIn sequence
python voice_engine/voice.py \
  --corpus voice_engine/samples/corpus \
  --research voice_engine/samples/research_input.md

# Produce a research report front end
python research_engine/research.py \
  --input research_engine/samples/brief_input.md \
  --contributors research_engine/samples/contributors.csv
```

Each tool ships with sample inputs so the commands above work out of the box.

---

## Authentication

All Claude calls go through `shared/llm.py`, which shells out to `claude -p` in headless mode. This uses your Claude Pro or Max subscription — no API key, no per-token billing.

`shared/llm.py` checks for `ANTHROPIC_API_KEY` on startup and refuses to run if it is set. That variable silently reroutes billing to the API account. Keep it unset.

Confirm your subscription is active before any run:
```bash
claude /status
```

---

## How it works

```
shared/
├── llm.py          ← all Claude calls go here (claude -p, subscription auth)
├── fetch.py        ← URL fetch and parse (requests + BeautifulSoup)
├── antislop.py     ← hard prose quality gate (detect violations + Claude rewrite)
├── report.py       ← self-contained HTML report renderer
└── adapters/
    ├── engines.py  ← Claude active; OpenAI/Perplexity/Gemini stubbed
    ├── search.py   ← URL discovery; manual input default
    └── enrichment.py ← contact enrichment; manual input default
```

Every tool imports from `shared/`. No logic is duplicated. The adapter pattern means each tool works fully for free with the manual default, and a paid upgrade (Clay, Apollo, a search API) is a one-line config change.

---

## Optional paid adapters

The tools work without any of these. Set environment variables to activate them.

| Adapter | Purpose | Variables |
|---|---|---|
| OpenAI / Perplexity / Gemini | Multi-engine AI queries in `brief_generator` and `entity_auditor` | `OPENAI_API_KEY`, `PERPLEXITY_API_KEY`, `GEMINI_API_KEY` |
| Clay | Contact enrichment in `pipeline_engine` and `research_engine` | `CLAY_API_KEY` + `ENRICHMENT_SOURCE=clay` |
| Apollo | Contact enrichment | `APOLLO_API_KEY` + `ENRICHMENT_SOURCE=apollo` |
| CRM CSV | Contact enrichment from a CRM export | `ENRICHMENT_SOURCE=csv` + `CRM_EXPORT_PATH=...` |
| Search API | URL discovery in `brief_generator` | `SEARCH_API_KEY` + `SEARCH_PROVIDER=brave\|exa\|serpapi` |

See `.env.example` for the full list. Never set `ANTHROPIC_API_KEY`.

---

## Repo structure

```
gtm-engine/
├── CLAUDE.md               ← shared conventions (read by Claude Code)
├── README.md               ← this file
├── antislop_rules.md       ← prose quality rules used by all tools
├── requirements.txt
├── test_shared.py          ← smoke test for the shared layer
├── .env.example
├── docs/
│   └── BUILD_GUIDE.md      ← step-by-step build prompts
├── shared/                 ← shared utilities (never copy into a tool)
├── entity_auditor/
├── pipeline_engine/
├── brief_generator/
├── voice_engine/
├── research_engine/
└── outputs/                ← all generated artifacts (gitignored)
```

---

## Rate limits

Claude Pro limits are tighter than Max. A full run of `voice_engine` (14 posts + anti-slop rewrites) makes roughly 30 Claude calls — space them out or use Max if you hit a limit. The tools surface rate-limit messages plainly and tell you to wait rather than failing silently.

> **Note (after June 15 2026):** subscription usage from `claude -p` is expected to draw from a separate monthly Agent SDK credit pool rather than the interactive limit. Still subscription billing, not API billing. Check `claude /status` to see current limits.
