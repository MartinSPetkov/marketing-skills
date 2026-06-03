# Usage Guide

How to use each of the five GTM Engine tools, when to use the terminal versus Claude Code chat, and what to do with the outputs.

---

## Terminal vs Claude Code chat — which to use?

**Use the terminal for:**
- Real runs on real data
- Demo recordings (you see every stage print in real time)
- Anything you want to run repeatedly with different inputs

**Use Claude Code chat for:**
- Trying a tool for the first time without memorising flags
- Iterating on inputs ("re-run entity_auditor on this URL instead")
- Asking Claude to explain or improve an output after the run
- Chaining tools ("run entity_auditor, then use the findings to brief_generator")

In Claude Code chat, just describe what you want:

> "Run entity_auditor on gotcatalyst.com and tell me the top two gaps."

> "Run pipeline_engine on my engagements CSV and show me the top five leads."

Claude will call the correct bash command and show you the output. You do not need to remember flags.

Both modes run exactly the same Python code — Claude Code chat just types the terminal command for you.

---

## Before your first run

```bash
# From the repo root every time you open a new terminal
source .venv/bin/activate
unset ANTHROPIC_API_KEY
claude /status          # confirm subscription is active
```

If `claude /status` shows your subscription, you are ready. If it shows API key auth, run `unset ANTHROPIC_API_KEY` and check again.

---

## entity_auditor

**What it does:** Audits a brand's entity authority — how well AI engines can identify and independently verify it as a distinct organisation. This is not a page-level SEO audit. It targets the entity layer: the structured, verifiable signals that make a brand citable.

**When to use it:**
- Before pitching a B2B prospect ("I ran this on your site cold — here is what I found")
- On your own brand to understand your AI visibility gaps
- As the first step before running `brief_generator` (entity gaps and content gaps are related)

**Run:**
```bash
python entity_auditor/entity_audit.py --brand "Acme" --url "https://acme.com"

# With an explicit about page (auto-discovered if omitted):
python entity_auditor/entity_audit.py \
  --brand "Acme" \
  --url "https://acme.com" \
  --about-url "https://acme.com/about"
```

**What you get** (in `outputs/acme/`):
- `report.html` — open in any browser. Shows the score (A–F across four dimensions), gap analysis in plain language, and three fix assets.
- `organization.jsonld` — paste into the site's `<head>`. Validate at [Google Rich Results Test](https://search.google.com/test/rich-results) before deploying.

**What to do with the output:**
1. Open `report.html`. Read the headline finding and the gap analysis.
2. Copy the Organisation JSON-LD into the site's `<head>`. Replace every `[BRACKETED_PLACEHOLDER]` with a real verified URL first.
3. Copy the entity description to Wikidata, Crunchbase, and any directory that asks for a company description. Identical wording across sources strengthens the entity signal.
4. Work through the directory list in order. The first three matter most.

**Good demo targets:** a brand you know well (so you can speak to the gaps), or a live prospect on a discovery call. Run it cold — the finding lands in under a minute.

---

## pipeline_engine

**What it does:** Takes a list of people who engaged with content and turns it into a ranked warm-outreach list, with personalised message drafts for the top tier and a content attribution rollup that shows which pieces drove the most qualified leads.

**When to use it:**
- After publishing content and collecting engagement signal
- At the start of an outreach cycle to prioritise who to contact and in what order
- Any time you want to close the loop between content and pipeline

**Run:**
```bash
python pipeline_engine/pipeline.py \
  --icp pipeline_engine/samples/icp.md \
  --engagements pipeline_engine/samples/engagements.csv \
  --sender "Your Name, Your Title at Your Company"
```

**Preparing your inputs:**

*ICP file:* plain text or markdown. State target roles, company size, industry, and any hard disqualifiers. Two to four sentences is enough. See `pipeline_engine/samples/icp.md`.

*Engagement CSV:* export this from your CRM, LinkedIn analytics, or content platform. Required columns: `name`, `title`, `company`, `company_size`, `public_url`, `engagement_type`, `engagement_date`, `content_source`. The tool does not scrape LinkedIn or connect to any CRM — it reads a file you provide.

*Sender:* a short string that signs the outreach drafts. Use `"First Last, Title at Company"`.

**What you get** (in `outputs/pipeline_TIMESTAMP/`):
- `report.html` — HTML dashboard: ranked lead table, per-lead scores, outreach drafts for the top tier, content attribution rollup at the bottom.
- `leads.csv` — full data export, one row per lead with all scores.
- `leads.md` — markdown table for pasting into Notion or Docs.

**What to do with the output:**
1. Open `report.html`. The top-tier leads have drafted messages — review and personalise before sending.
2. Look at the content attribution rollup at the bottom. It answers "which content produced the most qualified warm leads."
3. Disqualified leads appear at the bottom of the table with a reason. Review a few to check the scoring logic matches your intuition, then tune the weights in `pipeline.py` if needed.

**Honest limits:** the tool scores and drafts from whatever is in the CSV. Thin enrichment data produces thinner personalisation. Connecting Clay or Apollo (via the adapter) improves message quality. The README documents exactly how.

---

## brief_generator

**What it does:** Takes a single buyer-intent query and produces a full AEO content brief plus a valid JSON-LD schema file. The brief is engineered for AI engine citation: answer-first, structured, FAQ-complete, schema-marked.

**When to use it:**
- Before writing any piece of content meant to show up in AI search results
- For a client to show them exactly what a citable page looks like vs what they have now
- As a repeatable brief format for a content team or writer

**Run:**
```bash
python brief_generator/brief.py \
  --query "best contract testing tools" \
  --context brief_generator/samples/context.md

# With competitor/reference URLs for a sharper gap analysis:
python brief_generator/brief.py \
  --query "best contract testing tools" \
  --context brief_generator/samples/context.md \
  --urls brief_generator/samples/urls.txt
```

**Preparing your inputs:**

*Context file:* four things — company name, one-line positioning, 2–4 sentence description, homepage URL. See `brief_generator/samples/context.md` for the format. Copy it and edit it for your company.

*URLs file (optional):* one competitor or reference URL per line, lines starting with `#` ignored. Paste in 2–5 strong pages that currently rank for the query. The tool fetches them and identifies gaps.

**What you get** (in `outputs/<query-slug>/`):
- `brief.md` — full content brief: answer-first summary (verbatim-citable), H2/H3 outline, FAQ block, statistics with source placeholders, named entities, link suggestions, credibility signals.
- `schema.jsonld` — valid JSON-LD in the correct type for the page (FAQPage, Article, HowTo, or DefinedTerm).

**What to do with the output:**
1. Replace every `[SOURCE NEEDED: ...]` placeholder with a real citation before writing.
2. Use the answer-first summary verbatim in the first 100 words of the page — this is the block an AI engine can lift.
3. Give the brief to a writer (or write to it yourself). The outline is the skeleton.
4. Paste `schema.jsonld` into the page `<head>`. Validate it at [Google Rich Results Test](https://search.google.com/test/rich-results) before publishing.

---

## voice_engine

**What it does:** Takes a folder of an executive's existing posts and a research finding, and produces a 14-day LinkedIn sequence written in that person's voice. Every post passes through a hard anti-slop gate: banned words, banned phrases, and AI tells are detected and rewritten. The before/after HTML shows both drafts side by side.

**When to use it:**
- For an exec who has content ideas but no time to write
- For a ghostwriter who needs to match a voice quickly and at volume
- To demonstrate the difference between generic AI writing and voice-matched, gate-passed output

**Run:**
```bash
python voice_engine/voice.py \
  --corpus voice_engine/samples/corpus \
  --research voice_engine/samples/research_input.md

# With custom anti-slop rules:
python voice_engine/voice.py \
  --corpus my_exec/corpus \
  --research my_exec/finding.md \
  --rules antislop_rules.md

# Force re-analysis of the corpus (after adding new posts):
python voice_engine/voice.py \
  --corpus my_exec/corpus \
  --research my_exec/finding.md \
  --reanalyze
```

**Preparing your inputs:**

*Corpus folder:* 10–15 of the exec's existing posts as `.txt` or `.md` files, one post per file. Copy and paste from LinkedIn — do not scrape. 5 posts minimum; fewer than 5 produces a weaker fingerprint.

*Research input:* a short markdown file with the finding or stat to build the sequence around. One paragraph is enough. See `voice_engine/samples/research_input.md`.

*Voice profile caching:* after the first run, a `voice_profile.json` is written to the corpus folder. Subsequent runs load it instead of re-analysing — fast. If you add posts to the corpus, pass `--reanalyze` to regenerate it.

**What you get** (in `outputs/voice_TIMESTAMP/`):
- `before_after.html` — side-by-side view of every raw draft and its gate-passed final. The key demo artifact — open this in a browser and scroll through it.
- `posts/day_01.md` … `posts/day_14.md` — individual final posts, ready to copy-paste into LinkedIn or a scheduling tool.
- `calendar.md` — one-line summary per day: date, funnel stage, opening line.
- `hooks.md` — the hook bank (12 opening lines generated before sequencing).
- `voice_profile.json` — the extracted voice fingerprint in JSON.

**What to do with the output:**
1. Open `before_after.html` — read a few before/after pairs to check the voice is landing. If the "after" posts still read generically, review the corpus: add more distinctive posts and re-run with `--reanalyze`.
2. Review the calendar for pacing. Adjust the day ordering if the buyer-journey arc needs tuning.
3. Copy each final post from `posts/day_XX.md` directly. No rewriting should be needed — that is the point of the gate.

**Note:** the sample research figures are invented. Replace them with real data before publishing.

---

## research_engine

**What it does:** Produces the front end of an original peer research report — the part that takes the longest and is hardest to start: a defensible insight angle, a survey questionnaire designed to surface quotable statistics, a section-by-section report outline, and personalised contributor invitations for each target account.

**When to use it:**
- When a client wants to run original research as a pipeline play
- To get into rooms with target accounts who will not take a cold call (the ask is a research contribution, not a sales call)
- To produce a credible asset that positions the brand as the category authority

**Run:**
```bash
# With contributors CSV:
python research_engine/research.py \
  --input research_engine/samples/brief_input.md \
  --contributors research_engine/samples/contributors.csv

# Contributors entered interactively (prompted for each one):
python research_engine/research.py \
  --input research_engine/samples/brief_input.md
```

**Preparing your inputs:**

*Brief input file:* a markdown file with four sections — research category and theme, company running the research, target ICP for respondents, and optional reference URLs. See `research_engine/samples/brief_input.md`. The reference URLs are fetched and synthesised to ground the insight angle; leave them blank to generate the angle from the theme alone.

*Contributors CSV:* columns are `name`, `role`, `company`, `public_url`, `notes`. The `notes` column is a one-line context hook used to personalise the invitation ("Flowstate recently moved to freemium"). The `public_url` is fetched for additional context. See `research_engine/samples/contributors.csv`.

**What you get** (one markdown file in `outputs/research_engine/<slug>/`):
- `report_package.md` — four sections: insight angle (defensible + contrarian), survey questionnaire (8–12 questions), report outline (with `[SURVEY DATA]` and `[CONTRIBUTOR QUOTE]` placeholders), contributor invitations (one per person, anti-slop gated).

**What to do with the output:**
1. Read the insight angle section. Choose between the defensible angle (safer, evidence-grounded) and the contrarian angle (bolder, more memorable). Brief your research on whichever you pick.
2. Send the survey to an actual survey platform (Typeform, Tally, etc.). The questions are ready to paste.
3. Send each contributor invitation as written. Replace `[PLACEHOLDER]` facts before sending. The invitations are framed as peer research asks — do not add sales language.
4. Use the report outline once survey data comes back. Drop real statistics and quotes into the `[SURVEY DATA]` and `[CONTRIBUTOR QUOTE]` slots.

**Honest limits:** the tool generates the invitations but does not find email addresses. Real contact finding requires a paid tool (Clay, Apollo). The enrichment adapter is already wired — set one environment variable to activate it.

---

## Combining the tools

The tools are designed to be used in sequence, not in isolation.

**New brand or prospect:**
1. `entity_auditor` — find the entity gap
2. `brief_generator` — find the content gap for the key query
3. Use both findings in a pitch or proposal

**Content-to-pipeline loop:**
1. `brief_generator` — brief the content piece
2. `voice_engine` — build the supporting LinkedIn sequence
3. `research_engine` — build the research asset to attract target accounts
4. `pipeline_engine` — score engagement from all three plays and draft warm outreach

**Demo sequence (5–7 minutes on camera):**
1. `pipeline_engine` first — it answers the revenue question. Show the ranked outreach list and the attribution rollup.
2. `entity_auditor` on a live prospect site — a finding in under a minute, nothing fabricated.
3. `brief_generator` — show the schema file in the Rich Results Test.
4. `voice_engine` — open `before_after.html` and scroll through a few before/after pairs.

---

## Troubleshooting

**"The claude CLI was not found on PATH"**
Install it: `npm install -g @anthropic-ai/claude-code`, then `claude login`.

**"ANTHROPIC_API_KEY is set"**
Run `unset ANTHROPIC_API_KEY` and retry.

**Empty or garbled output from a Claude call**
Usually a rate limit. The tool will say so. Wait 60 seconds and retry. On Pro, space out tool runs. On Max, limits are significantly higher.

**Wikidata returns no entity for my brand**
Expected for smaller or newer companies. The entity_auditor continues without it and scores entity presence accordingly. Creating a Wikidata entry is one of the fixes the report recommends.

**A fetch returns an error for a URL**
Some sites block programmatic requests. The tool skips the fetch and continues — it will note the failure in the console and in the report. Pass a different URL or check the site manually.

**JSON-LD fails Google's Rich Results Test**
Check for unclosed brackets or commas. The most common cause is a placeholder string that contains a character not valid in JSON. Replace the placeholder with a real URL and re-validate.
