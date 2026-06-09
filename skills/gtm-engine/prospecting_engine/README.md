# Prospecting Engine

Trigger-based outbound prospecting. Give it a list of target accounts and a config file. It researches each account, detects the strongest reason to reach out (an AI-search visibility gap, a funding round, a new exec hire, a product launch), drafts a compliant personalized engagement plan, and runs the sequence through a state machine. In dry-run it produces the full output with nothing sent.

## Run command

```bash
python prospecting_engine/prospector.py run \
    --config prospecting_engine/samples/prospector_config.md \
    --accounts prospecting_engine/samples/target_accounts.csv \
    --replies prospecting_engine/samples/replies_fixture.csv \
    --dry-run
```

Outputs go to `outputs/prospecting_catalyst/`.

## What it produces

| File | Contents |
|---|---|
| `prospecting_plan.md` | Top accounts in full detail: research summary, trigger, AI-visibility wedge, score breakdown, all staged messages |
| `prospecting_queue.html` | Open in browser. Summary chips, ranked table with tier/trigger/wedge/status/first-action preview, disqualified section, compliance footer |
| `bookings/*.ics` | One calendar invite per booked meeting |
| `state.json` | Machine-readable state for every account |

## Pipeline stages

1. **Ingest** — reads accounts CSV and config
2. **Trigger detection** — classifies the trigger type and strength for each account
3. **Wedge generation** — checks AI-search visibility gap; leads with it when present
4. **ICP scoring** — Claude scores each account against the ICP; disqualifies clear misfits
5. **Composite scoring** — combines fit, trigger strength, and wedge clarity into one score and a tier (Hot / Warm / Cool)
6. **Engagement plans** — drafts warm-up comment, connection note, message 1, message 2, and email for each account; all prose through the anti-slop gate
7. **State machine** — advances each account through the sequence; handles positive reply (booked), negative reply (stopped), no reply (advance); enforces daily caps
8. **Outputs** — writes all files to the output folder

## Inputs

### `target_accounts.csv`

| Column | Description |
|---|---|
| company | Company name |
| domain | Company domain |
| industry | Industry description |
| company_size | Headcount |
| stage | Funding stage |
| target_persona_name | Full name of the target contact |
| target_persona_title | Their title |
| profile_url | Their LinkedIn URL (for reference; never scraped) |
| trigger_type | `funding`, `new exec`, `hiring`, `launch`, `content`, `ai_visibility`, `none` |
| public_signal | One sentence describing the public evidence for the trigger |
| ai_visibility_signal | AI search visibility observation (leave blank if none) |
| recent_post_excerpt | A recent public post excerpt if one exists (blank = no warmup comment) |

### `prospector_config.md`

Plain Markdown with sections for sender identity, ICP, trigger priorities, sequence definition, daily caps, and scoring weights. See `samples/prospector_config.md`.

### `replies_fixture.csv` (dry-run only)

Simulates replies so the state machine and booking can be shown offline:

```
name,touch,reply_text,sentiment
Priya Shah,msg1,"Yes, send the full gap. Free Thursday?",positive
Sara Quinn,msg1,"Interesting, but we just kicked off a rebrand. Circle back in Q3.",negative
```

Leave blank or omit to run with no simulated replies.

## Compliance

Discovery is from the provided account list and public web research only. The engine never scrapes LinkedIn to discover people. All LinkedIn actions (warm-up comment, connection note, messages) are staged for human approval by default. Nothing is sent in dry-run.

The live send route (`--live` flag) uses a single sanctioned API (Unipile) with daily caps enforced in code. Specific, researched personalization is the compliance strategy: irrelevant volume is what triggers spam reports.

## Adapters (free by default)

| Adapter | Default (free) | Paid upgrade |
|---|---|---|
| AI visibility check | Classifies the `ai_visibility_signal` field you provide | Live domain fetch + entity audit (same logic as `entity_auditor`) |
| ICP scoring | Claude via subscription (`shared/llm.py`) | Same — no upgrade needed |
| Live sends | Not available (dry-run only) | Unipile API (`UNIPILE_API_KEY` in `.env`) |

## Setup

```bash
# From the repo root
pip install -r requirements.txt        # or use .venv/bin/pip
claude login                           # Pro or Max subscription
claude /status                         # confirm subscription is active
unset ANTHROPIC_API_KEY                # must not be set
```

No API key needed. The `claude` CLI must be on PATH.

## Anti-slop gate

All human-facing prose passes through `shared/antislop.py` before being written. Rules in `antislop_rules.md` at the repo root: no em dashes, no filler openers or closing summaries, no hollow intensifiers, short declarative sentences, evidence first. The gate rewrites violations; it does not flag and pass.
