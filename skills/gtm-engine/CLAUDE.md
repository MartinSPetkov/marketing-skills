# CLAUDE.md

Shared context for this repo. Read this before building or editing any tool.

## What this repo is

A monorepo of five standalone GTM tools. Each one is a Python CLI that runs
independently and demonstrates AEO, content, and pipeline systems for B2B SaaS.
They share a small set of utilities in `shared/` and follow the same conventions so
the repo reads as one engineered system, not five scripts.

The five tools:

- `pipeline_engine/`: turns a list of engaged contacts into a prioritized, personalized
  warm-outreach list and attributes each lead to the content that surfaced them. The
  revenue loop, closed.
- `brief_generator/`: turns a buyer-intent query into an AEO content brief plus a
  ready-to-paste JSON-LD schema file.
- `entity_auditor/`: audits a brand's entity authority (how recognizable it is to AI
  engines) and generates the fix assets.
- `voice_engine/`: turns a research input into a 14-day LinkedIn sequence in a specific
  executive's voice, with a hard anti-slop gate on every post.
- `research_engine/`: turns a category into the front end of an original research
  report: insight angle, survey, outline, and personalized contributor invites.

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
├── .env.example
├── requirements.txt
├── shared/
│   ├── llm.py                # wraps `claude -p` (subscription auth, no API key)
│   ├── fetch.py              # URL fetch + parse (requests + BeautifulSoup)
│   ├── antislop.py           # reusable anti-slop gate
│   ├── report.py             # self-contained HTML report helper
│   └── adapters/
│       ├── engines.py        # Claude active; OpenAI/Perplexity/Gemini stubbed
│       ├── search.py         # optional URL discovery; manual input default
│       └── enrichment.py     # optional contact enrichment; manual default
├── pipeline_engine/          # the revenue loop, closed
├── entity_auditor/           # entity authority audit + fixes
├── brief_generator/          # AEO content brief + schema
├── voice_engine/             # exec voice content + anti-slop gate
├── research_engine/          # original research front end
└── outputs/                  # generated artifacts (gitignored)
```

## Build order

Build `shared/` first (`llm.py`, `fetch.py`, `antislop.py`, `report.py`, then the
adapters). Then build one tool end to end and confirm it runs on its sample before
starting the next. Recommended order: `entity_auditor` to validate the shared stack on
a simple tool, then `pipeline_engine` while the stack is fresh, then `brief_generator`,
`voice_engine`, `research_engine`. Do not build all five in parallel.
