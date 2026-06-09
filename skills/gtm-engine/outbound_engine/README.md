# Outbound Engine

Signal-to-meeting engine for inbound engagement. Give it engagement data from your LinkedIn posts and a config file. It groups engagements by person, scores each lead on ICP fit and intent signal, drafts a personalized multi-touch sequence referencing the exact post and comment, advances every lead through a state machine, and books a meeting when a positive reply lands. In dry-run it produces the full output with nothing sent.

## Run command

```bash
python outbound_engine/outbound.py run \
    --config outbound_engine/samples/outbound_config.md \
    --posts outbound_engine/samples/posts.csv \
    --engagements outbound_engine/samples/engagements.csv \
    --replies outbound_engine/samples/replies_fixture.csv \
    --dry-run
```

Outputs go to `outputs/outbound_catalyst/`.

## What it produces

| File | Contents |
|---|---|
| `sequences.md` | Top leads in full detail: score breakdown, all staged messages per lead |
| `approval_queue.html` | Open in browser. Summary chips, ranked lead table with fit/intent/tier/source/status/first-touch preview, disqualified section, post attribution chart |
| `bookings/*.ics` | One calendar invite per booked meeting |
| `state.json` | Machine-readable state for every lead |

## Pipeline stages

1. **Ingest** — reads posts, engagements, config
2. **Group by person** — merges multiple engagements per person into one lead; a person who commented on two posts is one lead with combined signal
3. **Score** — ICP fit via Claude (shared scoring), intent via formula (engagement type × recency × post topic × repeat bonus); composite score and tier (Hot / Warm / Cool)
4. **Draft sequences** — connection note (under 300 chars), message 1, message 2, email per qualified lead; every message references the specific post and, where present, the comment; all prose through the anti-slop gate
5. **State machine** — advances each lead through `connection_sent → msg1 → msg2 → email`; enforces daily caps from config
6. **Reply handling** — positive reply books a meeting and stops the sequence; negative reply stops politely; no reply advances
7. **Attribution** — which posts produced the most qualified leads and bookings
8. **Outputs** — writes all files to the output folder

## Inputs

### `posts.csv`

| Column | Description |
|---|---|
| post_id | Short ID (P1, P2, …) |
| date | Post date (YYYY-MM-DD) |
| topic | Short topic label |
| text | Full post text |

### `engagements.csv`

| Column | Description |
|---|---|
| engagement_id | Row ID |
| name | Person's full name |
| title | Job title |
| company | Company name |
| company_size | Headcount |
| profile_url | LinkedIn profile URL (for reference only; never accessed) |
| post_id | Which post they engaged with |
| engagement_type | `comment`, `repost`, or `like` |
| comment_text | Comment text (blank if repost/like) |
| engagement_date | Date of engagement (YYYY-MM-DD) |

### `outbound_config.md`

Sender identity, ICP, sequence day offsets, daily caps, and scoring weights. See `samples/outbound_config.md`.

### `replies_fixture.csv` (dry-run only)

```
name,touch,reply_text,sentiment
Daniel Okoye,msg1,"Yes, got time Thursday?",positive
Aisha Bello,msg1,"Maybe Q3.",negative
```

## Intent scoring formula

```
intent = max(engagement_type_score × recency_score × post_intent_score) + repeat_bonus
```

- Engagement type: comment 1.0, repost 0.6, like 0.3
- Recency: ≤7 days 1.0, ≤14 days 0.6, older 0.2
- Post intent: AI-search topic 1.0, content/pipeline 0.6, other 0.3
- Repeat bonus: +0.2 per extra post engaged (capped at +0.4)

Composite score = `fit_weight × fit_score + intent_weight × intent_score` (both 0-100 after normalisation).

## Compliance

LinkedIn's User Agreement prohibits unauthorized automation. This engine is human-in-the-loop by default. Every touch is staged for human approval before it is sent. The live send route (`--live`) uses a single sanctioned API (Unipile) with safe daily caps enforced in code.

## Adapters (free by default)

| Adapter | Default (free) | Paid upgrade |
|---|---|---|
| ICP scoring | Claude via subscription | Same — no upgrade needed |
| Live sends | Not available (dry-run only) | Unipile API (`UNIPILE_API_KEY` in `.env`) |

## Setup

```bash
pip install -r requirements.txt
claude login
claude /status
unset ANTHROPIC_API_KEY
```
