# GTM Engine

Seven standalone Python CLI tools for B2B SaaS go-to-market. Each runs independently on a single command. They share a small common layer in `shared/` and follow the same conventions, so the repo reads as one system.

All model calls run on a **Claude Pro or Max subscription** — no API key, no per-token billing.

---

## The seven tools

### Demand creation

| Tool | What it does | Run command |
|---|---|---|
| `entity_auditor` | Audits a brand's entity authority — how recognizable it is to AI engines — and generates the fix assets: JSON-LD schema and a structured data snippet | `python entity_auditor/entity_audit.py --brand "Acme" --url https://acme.com` |
| `brief_generator` | Turns a buyer-intent query into an AEO content brief plus a ready-to-paste JSON-LD schema file | `python brief_generator/brief.py --query "best contract testing tools"` |
| `voice_engine` | Turns a research input into a 14-day LinkedIn sequence in a specific executive's voice, with a hard anti-slop gate on every post | `python voice_engine/voice.py --input voice_engine/samples/voice_input.md` |
| `research_engine` | Turns a category into the front end of an original research report: insight angle, survey, outline, and personalized contributor invites | `python research_engine/research.py --input research_engine/samples/research_input.md` |

### Demand capture

| Tool | What it does | Run command |
|---|---|---|
| `pipeline_engine` | Turns a list of engaged contacts into a prioritized, personalized warm-outreach list and attributes each lead to the content that surfaced them | `python pipeline_engine/pipeline.py --input pipeline_engine/samples/leads.csv --icp pipeline_engine/samples/icp.md` |

### Outbound (two-tool family)

| Tool | What it does | Run command |
|---|---|---|
| `outbound_engine` | Signal-to-meeting engine. Turns people who engaged with LinkedIn posts into scored leads, drafts a personalized multi-touch sequence referencing the exact post and comment, and books a meeting on a positive reply | `python outbound_engine/outbound.py run --config outbound_engine/samples/outbound_config.md --posts outbound_engine/samples/posts.csv --engagements outbound_engine/samples/engagements.csv --replies outbound_engine/samples/replies_fixture.csv --dry-run` |
| `prospecting_engine` | Trigger-based cold outbound. Takes a list of target accounts, detects the strongest reason to reach out (AI-search gap, funding, new exec, launch), drafts a compliant personalized engagement plan, and runs every account through a sequence state machine | `python prospecting_engine/prospector.py run --config prospecting_engine/samples/prospector_config.md --accounts prospecting_engine/samples/target_accounts.csv --replies prospecting_engine/samples/replies_fixture.csv --dry-run` |

---

## Setup

```bash
# 1. Clone and install
git clone <repo-url>
cd gtm-engine
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Authenticate with your Claude subscription
claude login          # choose Claude.ai, sign in with your Pro or Max plan
claude /status        # confirm "Subscription" is shown as the active auth method

# 3. Make sure no API key is set
unset ANTHROPIC_API_KEY   # must not be set — it silently switches billing to API
```

No Anthropic API key is needed. The `claude` CLI must be installed and on PATH:

```bash
npm install -g @anthropic-ai/claude-code
```

---

## How authentication works

Every tool shells out to `claude -p "<prompt>"` via `shared/llm.py`. This uses your Pro or Max subscription, not a pay-per-token API key. If `ANTHROPIC_API_KEY` is set in the environment, Claude Code bills your API account instead — the tools check for this on startup and refuse to run if it is present.

---

## Adapter pattern — free by default, paid optional

Every tool that could depend on a paid or external service uses an adapter in `shared/adapters/` with a working free default.

| Adapter | Free default | Optional paid upgrade |
|---|---|---|
| AI engine querying | Claude via subscription | OpenAI, Perplexity, Gemini (set key in `.env`) |
| Search / URL discovery | Manual URL input | Brave, Exa, or SerpAPI |
| Contact enrichment | Manual input from CSV | Clay, Apollo, or CSV export |
| Live outbound sends | Dry-run only (staged) | Unipile API (LinkedIn + email + calendar) |

Every tool runs fully for free. The paid path is a one-line config change, clearly labelled with `TODO` comments in the adapter files.

---

## Outputs

All generated artifacts go to `outputs/` (gitignored). HTML reports are self-contained with inline CSS — open directly in a browser, no server needed.

---

## Repo structure

```
gtm-engine/
├── CLAUDE.md                     # shared build instructions for Claude Code
├── README.md
├── antislop_rules.md             # prose quality rules (no em dashes, no filler, etc.)
├── requirements.txt
├── test_shared.py                # smoke tests for the shared layer
│
├── shared/                       # shared utilities, imported by all tools
│   ├── llm.py                    # all Claude calls go here (subscription auth, no API key)
│   ├── fetch.py                  # URL fetch + parse
│   ├── antislop.py               # anti-slop gate: detects violations, rewrites via Claude
│   ├── report.py                 # self-contained HTML report helper
│   ├── scoring.py                # ICP fit scoring (pipeline_engine + outbound tools)
│   ├── sequence.py               # sequence state machine (outbound_engine + prospecting_engine)
│   ├── ai_visibility.py          # AI-search visibility gap helper (prospecting_engine)
│   └── adapters/
│       ├── engines.py            # Claude active; OpenAI/Perplexity/Gemini stubbed
│       ├── search.py             # optional URL discovery; manual input default
│       ├── enrichment.py         # optional contact enrichment; manual default
│       └── outbound_send.py      # Unipile stub; dry-run by default
│
├── entity_auditor/               # entity authority audit + fix assets
├── brief_generator/              # AEO content brief + JSON-LD schema
├── voice_engine/                 # exec voice LinkedIn sequence
├── research_engine/              # original research report front end
├── pipeline_engine/              # warm-outreach list + content attribution
├── outbound_engine/              # inbound engagement → scored leads → sequences → bookings
├── prospecting_engine/           # cold outbound → triggers → engagement plans → bookings
│
├── docs/
│   ├── USAGE.md                  # per-tool usage guide; terminal vs Claude Code chat
│   ├── BUILD_GUIDE.md            # full build order and decisions
│   └── reference/                # example outputs used as format targets during build
│
└── outputs/                      # generated artifacts (gitignored)
```

Each tool directory contains:
- One CLI entry point (e.g. `entity_audit.py`, `outbound.py`)
- `README.md` with run command, pipeline stages, input format, and adapter table
- `samples/` with everything needed to run the tool out of the box

---

## Honesty in output

- No fabricated statistics, sources, citations, or quotes. Where a real source is needed, the output contains a clearly marked placeholder for the user to fill.
- When a step is skipped because a paid key is missing, the tool says so in the console and in the output file. No silent degradation.
- Outbound tools stage every action for human approval by default. Nothing is sent in dry-run.

---

## Rate limits

Claude Pro limits are tighter than Max. A full run of one of the larger tools (voice_engine generating 14 posts, outbound_engine drafting sequences for 6 leads) may hit a rate limit after several Claude calls. When that happens, the tool prints the message and you can re-run after a short wait. Max subscribers can run the full suite back to back without spacing.

---

## Compliance note (outbound tools)

Discovery in `prospecting_engine` is from the provided account list and public web research only — never LinkedIn scraping. Every LinkedIn action produced by both outbound tools is staged for human approval. The live send route (`--live` flag) uses a single sanctioned API (Unipile) with daily caps enforced in code. Specific, researched personalization is the compliance strategy: irrelevant volume is what triggers the spam reports that get accounts flagged.
