# CLAUDE.md

Shared context for this repo. Read this before building or editing any tool.

## What this repo is

A monorepo of seven standalone GTM tools. Each one is a Python CLI that runs
independently. They share a common layer in `shared/` and follow the same conventions
so the repo reads as one engineered system, not seven scripts.

The seven tools:

### Demand creation
- `entity_auditor/`: audits a brand's entity authority (how recognizable it is to AI
  engines) and generates the fix assets: JSON-LD schema and structured data snippet.
- `brief_generator/`: turns a buyer-intent query into an AEO content brief plus a
  ready-to-paste JSON-LD schema file.
- `voice_engine/`: turns a research input into a 14-day LinkedIn sequence in a specific
  executive's voice, with a hard anti-slop gate on every post.
- `research_engine/`: turns a category into the front end of an original research
  report: insight angle, survey, outline, and personalized contributor invites.

### Demand capture
- `pipeline_engine/`: turns a list of engaged contacts into a prioritized, personalized
  warm-outreach list and attributes each lead to the content that surfaced them.

### Outbound (two-tool family)
- `outbound_engine/`: signal-to-meeting engine. Turns people who engaged with LinkedIn
  posts into scored leads (ICP fit + intent signal), drafts a personalized multi-touch
  sequence referencing the exact post and comment, advances each lead through a state
  machine, and books a meeting on a positive reply.
- `prospecting_engine/`: trigger-based cold outbound. Takes a list of target accounts,
  detects the strongest reason to reach out (AI-search visibility gap, funding, new exec,
  product launch), drafts a compliant personalized engagement plan per account, and runs
  every account through a sequence state machine.

## Conventions (apply to every tool)

### Language and structure
- Python 3.11+. Each tool has one CLI entry point in its own directory and runs on
  its own.
- Shared logic lives in `shared/` and is imported, never copied into a tool.
- Each tool has its own `README.md` and a `samples/` folder, and runs out of the box
  on the included sample with no setup beyond the API key.

### LLM access (subscription, no API key)
This repo runs on a Claude Pro or Max subscription, not a pay-per-token API key.

- All model calls go through `shared/llm.py`. A tool never invokes Claude directly.
- `shared/llm.py` shells out to the Claude Code CLI in headless mode
  (`claude -p "<prompt>"`, adding `--output-format json` when structured output is
  needed) and reads the result from stdout. Do not use the `anthropic` SDK and do not
  call the Anthropic API. There is no API client in this repo.
- `ANTHROPIC_API_KEY` must NOT be set in the environment. If it is set, Claude Code
  bills the API account instead of the subscription. On startup `shared/llm.py` checks
  for it and refuses to run with a clear message if it is present.
- Authenticate once with `claude login` using Pro or Max credentials. Confirm with
  `claude /status` that the subscription is the active method.
- The model is a single config constant in `shared/llm.py`, passed via the `--model`
  flag. Set it once. Never hardcode a model string anywhere else.
- `shared/llm.py` owns: building the command, running the subprocess, parsing JSON
  output, basic retry on transient failure, and surfacing rate-limit messages plainly.
  Pro limits are tighter than Max, so a full four-tool batch may need spacing out.
- Prerequisite: the `claude` CLI must be installed and on PATH (it is, inside Claude
  Code). No API key, no `.env` entry for Claude.

### Adapter pattern (important)
Anything that could rely on a paid or external service is an adapter in
`shared/adapters/`, with a working free default and a clearly labelled optional paid
path.

- `engines.py` — AI-engine querying. Claude is the active default. OpenAI, Perplexity,
  and Gemini are stubbed with explicit TODO labels and require keys. If no key is
  present for an engine, skip it and say so in the output. Never pretend an engine ran.
- `search.py` — optional search API for URL discovery. Default is manual URL input,
  which always works.
- `enrichment.py` — optional contact enrichment. Default is manual contributor input.
- `outbound_send.py` — optional live send via Unipile (LinkedIn comment, connection,
  message, email, calendar). Default is dry-run: every action is staged for human
  approval and nothing is sent. The live path requires `UNIPILE_API_KEY` and the
  `--live` flag. Never called in dry-run.

The point of the pattern: every tool works fully for free, and the paid upgrade is a
one-line config change. State this honestly in each tool's README.

### Honesty in output (non-negotiable)
- Never fabricate a statistic, source, citation, or quote. Where a real source is
  needed, write a clearly marked placeholder for the user to fill.
- When a step is skipped because a paid key is missing, say so in the console and in
  the output file. Do not silently degrade.
- Schema must be valid JSON-LD. Tell the user to validate it with Google's Rich
  Results Test.

### Prose output
- Any human-facing prose (briefs, posts, invites, report copy) passes through
  `shared/antislop.py` before it is written to disk.
- Rules: no em dashes, no filler openers or summarising closers, no hollow
  intensifiers, short declarative sentences, evidence first.
- The anti-slop gate is a hard gate, not a flag. Failed text is rewritten, not just
  marked.

### Outbound compliance (non-negotiable)
The two outbound tools produce LinkedIn actions. These rules apply whenever touching
either tool:

- Never scrape LinkedIn to discover people or accounts. Discovery comes from the
  provided CSV and public web research only.
- Every LinkedIn action (comment, connection, message) is staged for human approval
  by default. Dry-run is the default mode and produces no sends.
- The live send path is a single sanctioned adapter (`outbound_send.py`) behind
  `--live` and `UNIPILE_API_KEY`. Daily caps are enforced in code before the adapter
  is ever called.
- Do not add any feature that auto-discovers or auto-acts on LinkedIn.

### What never to do
- Never set `ANTHROPIC_API_KEY` in this repo's environment. It silently switches
  billing from the subscription to the API account.
- Never scrape Google search results or LinkedIn. Use provided URLs, public APIs
  (e.g. Wikidata), or the labelled optional search adapter.
- Never block on a missing optional key. Degrade gracefully and report it.

### Demo-readiness
- Print each pipeline stage to the console as it runs, so a screen recording shows
  the system working rather than a black box.
- Reports are self-contained HTML with inline CSS, no server, openable directly in a
  browser.
- Every tool runs from a single command, documented at the top of its README, working
  on the included sample.

## Setup

```
pip install -r requirements.txt
claude login            # choose Claude.ai, log in with your Pro or Max plan
claude /status          # confirm the subscription is the active auth method
unset ANTHROPIC_API_KEY  # ensure no API key overrides the subscription
```

No Anthropic API key is needed. `.env.example` documents only the optional paid keys
for the non-Claude engines (OpenAI, Perplexity, Gemini), which stay stubbed by default.

Each tool's run command is at the top of its own README.

## Repo structure

```
gtm-engine/
├── CLAUDE.md
├── README.md
├── antislop_rules.md         # prose quality rules read by shared/antislop.py
├── .env.example
├── requirements.txt
├── test_shared.py            # smoke tests for the shared layer
├── shared/
│   ├── llm.py                # wraps `claude -p` (subscription auth, no API key)
│   ├── fetch.py              # URL fetch + parse (requests + BeautifulSoup)
│   ├── antislop.py           # hard anti-slop gate; reads antislop_rules.md
│   ├── report.py             # self-contained HTML report helper
│   ├── scoring.py            # ICP fit scoring; shared by pipeline_engine + outbound tools
│   ├── sequence.py           # sequence state machine; shared by outbound_engine + prospecting_engine
│   ├── ai_visibility.py      # AI-search visibility gap helper; used by prospecting_engine
│   └── adapters/
│       ├── engines.py        # Claude active; OpenAI/Perplexity/Gemini stubbed
│       ├── search.py         # optional URL discovery; manual input default
│       ├── enrichment.py     # optional contact enrichment; manual default
│       └── outbound_send.py  # Unipile stub; dry-run by default; never called without --live
├── entity_auditor/           # entity authority audit + fix assets
├── brief_generator/          # AEO content brief + JSON-LD schema
├── voice_engine/             # exec voice LinkedIn sequence + anti-slop gate
├── research_engine/          # original research report front end
├── pipeline_engine/          # warm-outreach list + content attribution
├── outbound_engine/          # inbound engagement → scored leads → sequences → bookings
├── prospecting_engine/       # cold outbound → triggers → engagement plans → bookings
├── docs/
│   ├── USAGE.md              # per-tool usage guide
│   ├── BUILD_GUIDE.md        # build order and decisions
│   └── reference/            # example outputs used as format targets
└── outputs/                  # generated artifacts (gitignored)
```

Each tool directory contains one CLI entry point, a `README.md`, and a `samples/`
folder with everything needed to run it out of the box.

## Shared modules — what each one owns

- `llm.py` — the only place Claude is called. Owns command building, subprocess
  execution, JSON envelope unwrapping, retry on transient failure, rate-limit messages.
- `fetch.py` — URL fetch + parse. Owns `_guard_url()` (blocks LinkedIn/Google scraping),
  link extraction (must run before `_extract_body()` which decomposes the DOM), body
  extraction, JSON-LD and FAQ extraction.
- `antislop.py` — `clean(text)` rewrites prose through Claude using rules in
  `antislop_rules.md`. `check(text)` returns violations. The gate always rewrites;
  it never just flags and passes.
- `report.py` — `render(title, sections)` produces a self-contained HTML file with
  inline CSS. No server required.
- `scoring.py` — `score_fit_batch(records, icp_text)` scores a list of dicts against
  an ICP in a single Claude call. Attaches `fit_score`, `fit_reason`, `disqualified`,
  `disqualify_reason` to each record. Used by `pipeline_engine` and both outbound tools.
- `sequence.py` — `SequenceState` dataclass and `simulate_dry_run()`. State order:
  `new → warmup → connection_sent → connected → msg1 → msg2 → email → booked/stopped/
  disqualified`. `outbound_engine` skips warmup (leads already engaged). Also owns
  `make_ics()` for calendar invites.
- `ai_visibility.py` — `check_visibility(account, dry_run=True)`. In dry-run, classifies
  the `ai_visibility_signal` field via a single Claude call; no network traffic. In live
  mode, fetches the domain and runs a gap check.

## Build order

The repo is fully built. If adding a new tool:

1. Confirm `shared/` has everything it needs; add to shared modules rather than
   copying logic into the tool.
2. Build one tool end to end and confirm it runs on its sample before starting the next.
3. Reuse `shared/scoring.py` for any ICP fit scoring.
4. Reuse `shared/sequence.py` for any multi-touch outbound sequence.
5. All prose through `shared/antislop.py`. All Claude calls through `shared/llm.py`.
