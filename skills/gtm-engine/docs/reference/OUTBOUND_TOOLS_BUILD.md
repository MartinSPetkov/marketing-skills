# Outbound tools: build addendum

Premise: the shared layer and the first five tools (entity_auditor, brief_generator,
pipeline_engine, voice_engine, research_engine) are already built. This adds the two
outbound tools on top: outbound_engine (inbound qualification) and prospecting_engine
(cold outbound). Build outbound_engine first, because prospecting_engine reuses its
sequence state machine.

---

## 0. Before you start

- Confirm subscription auth in the shell: `claude /status`, and `unset ANTHROPIC_API_KEY`.
- Both tools run fully offline in dry-run on the provided sample data. Dry-run is the default and all that is needed to build and demo.
- Place the sample inputs in each tool's samples/ folder, and hand Claude Code the example outputs as format targets. The full file list is at the end.

## 1. Reuse what already exists

- All Claude calls go through shared/llm.py.
- All human-facing prose goes through shared/antislop.py, reading antislop_rules.md at the repo root.
- HTML reports use shared/report.py.
- Fit and warmth scoring: reuse pipeline_engine's logic. If it already lives in shared/ (for example shared/scoring.py), import it. If it lives inside the pipeline module, refactor the reusable part into shared/scoring.py and import it from both places.
- AI-visibility wedge (prospecting only): reuse the entity_auditor and brief_generator logic. If they expose importable functions for the AI-visibility or gap check, import them. If not, refactor a small shared function (for example shared/ai_visibility.py) out of the existing code so all three use one implementation. Inspect those files before deciding.
- New shared module: outbound_engine puts its sequence state machine in shared/sequence.py, and prospecting_engine imports it.

## 2. Build order

1. outbound_engine (creates shared/sequence.py)
2. prospecting_engine (imports shared/sequence.py and the entity and brief logic)

---

## 3. Prompt: outbound_engine (inbound qualification)

```
Read CLAUDE.md first, then inspect the existing shared/ layer and the pipeline_engine tool, and reuse them. All Claude calls go through shared/llm.py (subscription via `claude -p`, no API key). All prose goes through shared/antislop.py (rules at antislop_rules.md in the repo root). HTML uses shared/report.py. The tool must run fully offline in dry-run with no network calls and no platform API. Dry-run is the default and all that is needed to build and demo.

Reuse pipeline_engine's fit and warmth scoring. If it is already in shared/scoring.py, import it; if it lives inside the pipeline module, refactor the reusable part into shared/scoring.py and import it from both places.

Build a Python command-line tool: a signal-to-meeting engine. It turns people who engaged with a set of LinkedIn posts into scored leads, drafts a personalized multi-touch sequence for each, advances them through a state machine, and books a meeting when a reply is positive. By default it sends nothing; it stages drafts in an approval queue.

Inputs (local, in samples/):
- posts.csv: post_id, date, topic, text.
- engagements.csv: engagement_id, name, title, company, company_size, profile_url, post_id, engagement_type (comment, repost, like), comment_text, engagement_date. One person can appear on multiple posts.
- outbound_config.md: sender identity, ICP, sequence definition (touches and day offsets), daily caps, booking link, scoring weights.
- replies_fixture.csv: name, touch, reply_text, sentiment. Dry-run only, to simulate replies so the state machine and booking can be shown offline.

Pipeline:
1. Ingest and group engagements by person; a person with multiple engagements is one lead with combined signal.
2. Signal scoring, each explained in one line: fit against the ICP (disqualify clear mismatches, reuse shared scoring), and intent weighting engagement type (comment > repost > like), recency, repeat engagement across posts, and the intent of the post engaged with. Weights in config, logic in one readable function. Combine into a score and a tier (Hot, Warm, Cool).
3. Draft a personalized sequence per qualified lead, in the sender's voice, every message through shared/antislop.py: a LinkedIn connection note (under 300 characters), message 1, message 2, and an optional email. Each references the specific post and, where present, the comment. No generic openers.
4. State machine per lead: new, connection_sent, connected, msg1, msg2, email, booked, replied_stopped, disqualified. Advance on the day offsets in config. Put the state machine in shared/sequence.py so prospecting_engine can reuse it.
5. Reply handling. In dry-run, read replies_fixture.csv: positive stops and books, negative stops politely, none advances.
6. Booking. On a positive reply, generate a .ics invite and record it. Use the booking link in the copy.
7. Pacing and caps. Enforce the daily connection and message caps from config even in dry-run.
8. Attribution: which posts produced the most qualified leads and booked meetings.

Outputs (to an output folder, print each stage to the console): sequences.md (per lead, score breakdown and full sequence), approval_queue.html (summary counts, ranked lead table, booked section, attribution section), bookings/ (one .ics per booked meeting), state.json.

One live route, do NOT build a menu. A single optional adapter shared/adapters/outbound_send.py for Unipile (LinkedIn send, email, calendar), behind a --live flag and a UNIPILE_API_KEY placeholder, a labelled stub with TODOs. In dry-run it is never called. Even in --live, require approval before any send and enforce caps.

In the README: LinkedIn's User Agreement prohibits unauthorized automation; the engine is human-in-the-loop by default; the live route is a single sanctioned API with safe caps. Match the format and quality of the provided example outputs (outbound_sequences.md and outbound_approval_queue.html).

Single command, e.g. `python outbound.py run --dry-run --config outbound_config.md`. Works out of the box on the included dummy data. Ask clarifying questions before you start.
```

---

## 4. Prompt: prospecting_engine (true outbound)

```
Read CLAUDE.md first, then inspect the existing shared/ layer, the entity_auditor and brief_generator tools, and shared/sequence.py created by outbound_engine. Reuse them. All Claude calls go through shared/llm.py (subscription via `claude -p`, no API key). All prose goes through shared/antislop.py (rules at antislop_rules.md in the repo root). HTML uses shared/report.py. The tool must run fully offline in dry-run with no network calls. Dry-run is the default.

For the AI-visibility wedge, reuse the entity_auditor and brief_generator logic. If they expose importable functions for the AI-visibility or gap check, import them; if not, refactor a small shared function (for example shared/ai_visibility.py) out of the existing code so all three use it. Inspect those files before deciding. Reuse shared/sequence.py for the state machine and reply handling.

Build a Python command-line tool: a trigger-based outbound prospecting engine. This is the cold, outbound counterpart to outbound_engine. outbound_engine qualifies people who already engaged with our posts. This engine goes after target accounts that have never engaged, finds a real reason to reach out, and drafts a compliant, personalized engagement plan.

Compliance is a hard requirement and a selling point. The engine NEVER scrapes LinkedIn to discover people. Discovery comes from a provided account list plus public web research only. Every LinkedIn action it produces is staged for human approval by default. Do not add any feature that auto-discovers or auto-acts on LinkedIn.

Inputs (local, in samples/):
- target_accounts.csv: company, domain, industry, company_size, stage, target_persona_name, target_persona_title, profile_url, trigger_type, public_signal, ai_visibility_signal, recent_post_excerpt. The signal fields hold public evidence so the tool runs offline in dry-run.
- prospector_config.md: ICP, sender identity and offer, trigger priorities, sequence definition, daily caps, booking link, scoring weights.
- replies_fixture.csv: name, touch, reply_text, sentiment. Dry-run only.

Pipeline:
1. Ingest target accounts.
2. Research and trigger detection. In dry-run, read the public_signal, ai_visibility_signal, and recent_post_excerpt fields. In live mode, fetch the provided public URLs via shared/fetch.py and, where a domain is given, run the entity and brief AI-visibility logic to generate the gap fresh. Classify trigger type and a strength score. Never scrape LinkedIn; use provided inputs and public company pages only.
3. Wedge generation. Where an AI-visibility gap exists, make it the lead hook, reusing the entity and brief logic. Otherwise lead with the strongest trigger (funding, new exec, hiring, launch).
4. Persona and fit. Score the account against the ICP and disqualify clear misfits.
5. Score and tier. Combine ICP fit, trigger strength, and wedge clarity into one score and a tier, each factor explained in one line.
6. Draft a compliant engagement plan per qualified account, every message through shared/antislop.py, each referencing the specific trigger or wedge: a warm-up comment on the prospect's recent public post (only if recent_post_excerpt is present, genuine, no pitch), a connection note under 300 characters tied to the trigger, message 1 leading with the observation or wedge, message 2, an optional email.
7. State machine and dry-run reply handling, reusing shared/sequence.py: positive stops and books, negative stops politely, none advances. Enforce daily caps.
8. Outputs (to an output folder, print each stage): prospecting_plan.md (per top account: research summary, trigger, wedge, persona, score breakdown, full staged plan), prospecting_queue.html (summary counts, ranked account table with trigger, wedge, persona, score, status, first-action preview, a disqualified section, and a compliance footer), bookings/ (one .ics per booked meeting), state.json.

One live route only, do NOT build a menu. A single optional adapter for Unipile (LinkedIn comment, connection, message, email, calendar) behind a --live flag and a UNIPILE_API_KEY placeholder, a labelled stub with TODOs. In dry-run it is never called. Even in --live, require approval before any action and enforce caps.

In the README, state plainly: discovery is from provided lists and public web only, never LinkedIn scraping; all LinkedIn actions are staged for human approval by default; the live route is a single sanctioned API with safe caps; specific, researched personalization is the compliance strategy. Match the format and quality of the provided example outputs (prospecting_plan.md and prospecting_queue.html).

Single command, e.g. `python prospector.py run --dry-run --config prospector_config.md`. Works out of the box on the included dummy data. Ask clarifying questions before you start.
```

---

## 5. Smoke test (these two tools)

- Run each from its single command on its sample data.
- Confirm neither makes a network call in dry-run, both stage everything for approval, and both enforce the daily caps.
- Confirm all drafted prose passed through the anti-slop gate (check a before and after, or spot-check for em dashes and filler).
- Confirm a positive reply in the fixture books a meeting and writes a .ics; a negative reply stops the sequence; no reply advances it.
- Confirm prospecting_engine leads with the AI-visibility wedge when present and reuses shared/sequence.py.
- Run `claude /status` to confirm you stayed on the subscription.

## 6. Compliance note (say this out loud when demoing)

Discovery is from provided lists and public web research only, never LinkedIn scraping.
Every LinkedIn action is staged for human approval. The only live send route is a single
sanctioned API behind a flag and a key, with safe daily caps enforced in code. Specific,
researched personalization is the compliance strategy, because irrelevant volume is what
triggers the spam reports that get accounts flagged. For an agency whose product depends
on live LinkedIn accounts, that posture is the point, not a caveat.

## 7. Loom note

Open on prospecting_engine: cold accounts in, researched triggers and an AI-visibility
wedge out, a compliant plan staged for approval, one meeting booked. Then outbound_engine
for the inbound half, with its post-attribution panel. The two together show capture and
create demand as one engine family, compliant, both booking meetings.

---

## 8. Relevant files (already prepared)

Place these into the repo; do not recreate them.

outbound_engine inputs, into outbound_engine/samples/:
- demo_inputs/outbound/posts.csv
- demo_inputs/outbound/engagements.csv
- demo_inputs/outbound/replies_fixture.csv
- demo_inputs/outbound/outbound_config.md

prospecting_engine inputs, into prospecting_engine/samples/:
- demo_inputs/prospecting/target_accounts.csv
- demo_inputs/prospecting/prospector_config.md
- demo_inputs/prospecting/replies_fixture.csv

Shared:
- antislop_rules.md at the repo root (already in use by your existing tools).

Example outputs, hand to Claude Code as format targets:
- example_outputs/outbound_sequences.md
- example_outputs/outbound_approval_queue.html
- example_outputs/booking_daniel_okoye.ics
- example_outputs/prospecting_plan.md
- example_outputs/prospecting_queue.html
