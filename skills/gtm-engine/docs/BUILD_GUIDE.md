# GTM Engine: Build Guide

One repo, five tools, built in Claude Code on your Claude subscription. No API key, no
pay-per-token billing. Work top to bottom: set up, then paste each prompt in order.

Keep `CLAUDE.md` at the repo root. It holds the shared conventions; these prompts
assume Claude Code reads it.

The five tools map to Catalyst's revenue loop: content gets buyers to find you, signal
gets scored, warm outreach turns signal into pipeline, and every lead traces back to the
content that moved it. `pipeline_engine` closes the loop; the other four feed it.

---

## 1. Prerequisites

- Claude Code installed, with a Claude Pro or Max subscription.
- Python 3.11+.
- An empty folder `gtm-engine/` with `CLAUDE.md` inside it.
- One real B2B SaaS prospect URL to test on (ideally a Catalyst-style company), so
  outputs are concrete rather than toy examples.
- Your anti-slop rules ready to paste (your martin-style ruleset), for the voice tool.

Authenticate on the subscription, not an API key:

```
claude login             # choose Claude.ai, log in with your Pro or Max plan
claude /status           # confirm the subscription is the active auth method
unset ANTHROPIC_API_KEY   # critical: if this is set, Claude Code bills the API account
```

Run `claude /status` again in any new terminal before building or demoing. That one
check is the difference between free and a surprise bill.

---

## 2. How to use these prompts

- Open Claude Code in `gtm-engine/`.
- Build in order: shared layer first, then one tool at a time. Do not build all five
  in parallel.
- Paste one prompt per focused session or turn. Let Claude ask its clarifying
  questions and answer them. That exchange is good Loom footage of you directing the
  build.
- After each tool, run it on its sample, then once on your real prospect input, and
  eyeball the output before starting the next tool.

Build order: shared layer, then `entity_auditor` (validates the shared stack on a simple
tool), then `pipeline_engine` (the headline build, while the stack is fresh), then
`brief_generator`, `voice_engine`, `research_engine`.

---

## 3. Prompt A: shared layer

```
Read CLAUDE.md first. Build ONLY the shared/ layer and the repo scaffolding. Do not build any tool yet.

Authentication is via the Claude subscription, not an API key. Do not use the anthropic SDK and do not read ANTHROPIC_API_KEY for auth.

Create:

- shared/llm.py: the single point all tools use to call Claude. It shells out to the Claude Code CLI in headless mode: run `claude -p "<prompt>"`, adding `--output-format json` and parsing the JSON when structured output is needed. Pass the model via the `--model` flag from one config constant at the top of the file. On first use, check whether ANTHROPIC_API_KEY is set in the environment, and if so refuse to run with a clear message explaining it would bill the API account instead of the subscription. Include basic retry on transient subprocess failure and surface rate-limit messages plainly. Expose two helpers: one returning plain text, one returning parsed JSON (prompt for JSON, parse, and retry once with a repair instruction if parsing fails).

- shared/fetch.py: fetch a URL and return clean parsed text plus structured elements (headings, any JSON-LD blocks, FAQ-style question/answer pairs, visible body), using requests + beautifulsoup4. Handle timeouts and bad status codes gracefully. Never fetch Google search results or LinkedIn.

- shared/antislop.py: a reusable gate. Given text and a rules file path, it runs the rules as a hard check, then runs a Claude rewrite pass (via shared/llm.py) to strip AI tells, and returns cleaned text. Rules: no em dashes, no filler openers or closers, no hollow intensifiers, short declarative sentences. Importable and runnable on any string.

- shared/report.py: render a self-contained HTML report with inline CSS, no external files and no server, given a title and a list of sections. Clean and presentable.

- shared/adapters/engines.py: query an AI engine and return its raw answer. Claude is the active default, routed through shared/llm.py. Add stubbed adapters for OpenAI, Perplexity, and Gemini with clear TODO labels that require their own keys. If a key is absent, skip that engine and report it rather than failing.

- shared/adapters/search.py: optional URL discovery. Default behaviour returns the URLs the user supplied manually. Leave a clearly labelled optional hook for a search API.

- shared/adapters/enrichment.py: optional contact enrichment. Default returns the contributor or contact info supplied manually. Labelled optional hook for a Clay or Apollo style source and a CRM export.

- requirements.txt: include requests and beautifulsoup4 and anything genuinely used. Do NOT include the anthropic SDK.

- .env.example: documents only the optional paid engine keys (OpenAI, Perplexity, Gemini). No Anthropic key.

- .gitignore: ignore outputs/ and .env.

After building, add a short paragraph to the repo README explaining that shared/llm.py authenticates through the Claude subscription via `claude -p` with no API key, and how to confirm with `claude /status`. Then stop and let me confirm it runs before we build any tool.

Ask clarifying questions before you start.
```

---

## 4. Prompt B: entity_auditor

```
Read CLAUDE.md first. Use the shared/ layer. All Claude calls go through shared/llm.py (subscription via `claude -p`, no API key).

Build a Python command-line tool that audits a brand's entity authority (how recognizable it is to AI engines as a distinct entity) and generates the assets to improve it. This is distinct from a page-level SEO audit; it audits the brand as an entity, which is the layer AI engines use to decide who to cite.

Inputs:
- A brand name and homepage URL.
- Optionally an about-page URL.

Pipeline:
1. On-site signals. Fetch the homepage and about page (via shared/fetch.py) and extract existing JSON-LD, specifically checking for Organization schema and sameAs links, plus the clarity and consistency of how the brand describes itself.
2. Off-site entity presence. Query the public Wikidata API to check whether the brand has an entity and how it is described. Check description consistency across the sources available. Keep each external check in its own module so more sources can be added later. Use only free public APIs; do not scrape sites that forbid it.
3. Scoring. Have Claude score the entity footprint across clear dimensions (entity presence, description consistency, structured-data completeness, third-party corroboration) and explain each gap in plain language. Pass explanations through shared/antislop.py.
4. Fix assets. Generate the deliverables: a valid Organization JSON-LD block with sameAs links, a consistent one-paragraph entity description suitable for a Wikidata entry and reuse across the web, and a prioritized list of authoritative directories and sources worth getting listed on for this category.

Outputs: a single self-contained HTML report (via shared/report.py) showing the score, the gaps with explanations, and the generated fix assets, plus the JSON-LD saved as its own file. Tell the user to validate the schema with Google's Rich Results Test.

This should run on any public B2B SaaS site cold, in under a minute, with no cost beyond subscription usage. Package for reuse: a single command like `python entity_audit.py --brand "..." --url "..."`, a README, and it should work out of the box on a real URL.

Ask clarifying questions before you start.
```

---

## 5. Prompt C: pipeline_engine (the revenue loop)

```
Read CLAUDE.md first. Use the shared/ layer. All Claude calls go through shared/llm.py (subscription via `claude -p`, no API key).

Build a Python command-line tool that turns a list of people who engaged with content into a prioritized, personalized warm-outreach list, and attributes each lead back to the content that surfaced them. This closes the loop from content to pipeline: content published, buyer discovered, signal scored, warm outreach drafted, every lead traced to the content that moved it.

Context: the value of content and AEO is only proven when it produces pipeline. This tool scores engaged contacts for fit and warmth, ranks them, drafts outreach, and shows which content is actually generating qualified warm leads.

Inputs:
- An ICP definition file: target roles, company size, industry, and any disqualifiers.
- An engagement list as a CSV that I provide or export: name, company, a public URL (company page or article), engagement type (e.g. liked, commented, downloaded, attended), recency, and which piece of content or which query surfaced them. Treat this CSV as the ingestion point; do not scrape LinkedIn or any CRM directly.

Pipeline:
1. Ingest and validate the engagement CSV.
2. Enrich each record from public info only: fetch the provided public URL via shared/fetch.py, and use shared/adapters/enrichment.py with its manual default. Leave a clearly labelled optional hook for a paid enrichment source (Clay, Apollo) and a CRM export. If enrichment data is thin, proceed with what is available and note it.
3. Fit scoring: have Claude score each lead against the ICP and explain the score in one line. Disqualify clear mismatches.
4. Warmth scoring: score engagement signals (type, recency, frequency) into a warmth tier (hot, warm, cool), with the logic in a single readable function so it is easy to tune.
5. Attribution: roll up which content or query produced the most qualified warm leads, so the output answers "which content is driving pipeline."
6. Prioritize and draft: rank leads by fit combined with warmth. For the top tier, draft a short personalized warm-outreach message that references the specific content they engaged with and one public detail about them. Pass all outreach prose through shared/antislop.py.

Outputs:
- A prioritized lead table (CSV and a markdown view): name, company, fit score, warmth tier, source content, and the drafted outreach message for the top tier.
- A content attribution summary: which content or queries produced the most warm qualified leads.
- A single self-contained HTML dashboard via shared/report.py showing the ranked list and the attribution summary. This is the key demo artifact.
- Print each pipeline stage to the console.

Be honest in the README about the boundary: live engagement capture and contact enrichment come from a CRM, LinkedIn, or paid tools like Clay and Apollo, which are paid or restricted. So the tool runs on a CSV I provide or export, and CRM and enrichment are the documented plug-in points. Ship a realistic sample CSV so it runs out of the box.

Package for reuse: a single command like `python pipeline.py --icp icp.md --engagements engagements.csv`, a README with the run command at the top, and the sample CSV.

Ask clarifying questions before you start.
```

---

## 6. Prompt D: brief_generator

```
Read CLAUDE.md first. Use the shared/ layer. All Claude calls go through shared/llm.py (subscription via `claude -p`, no API key).

Build a command-line tool in Python that generates an AEO-optimized content brief plus ready-to-paste schema markup for a single buyer-intent query. The goal is to produce the input a writer or a generation step needs to create a page that AI engines (ChatGPT, Claude, Perplexity, Gemini) will cite.

Context: AI engines cite content that is answer-first, well-structured, entity-rich, and marked up with schema.org JSON-LD. This tool turns one query into a brief that engineers for exactly that.

Inputs:
- A target query or topic (e.g. "best contract testing tools").
- Short company context: name, one-line positioning, and either a homepage URL or a 3-sentence description.
- An optional list of 3-5 competing or reference URLs the user pastes in.

Pipeline:
1. Recon. Fetch and parse any URLs the user provides (via shared/fetch.py), extracting headings, definitions, stats, FAQ blocks, and existing JSON-LD. Also query Claude (via shared/adapters/engines.py) with the target query to capture what an AI currently surfaces and which entities it names. Use the search adapter's manual-input default for URLs; do not auto-scrape Google.
2. Gap analysis. Have Claude compare what is already covered against the company's angle, and identify the unanswered sub-questions, the missing definitions, and the claims no competitor is making.
3. Brief assembly. Produce a markdown brief with: target query and search intent, recommended page type (definition page, comparison, FAQ, or guide), an answer-first summary block of 2-3 sentences an AI can lift verbatim, an H2/H3 outline, a set of FAQ question/answer pairs, the statistics and claims to include (with placeholders clearly flagged where the user must add a real source), the named entities to mention, internal and external linking suggestions, and the credibility signals to add. Pass the brief's own prose through shared/antislop.py.
4. Schema generation. Produce a valid JSON-LD file appropriate to the page type (FAQPage, Article, HowTo, or DefinedTerm), saved separately for dropping into the page head. Tell the user to validate it with Google's Rich Results Test.

Outputs: a markdown brief and a .jsonld file, written to an output folder named after the query. Print each pipeline stage to the console so a screen recording shows the system working.

Package for reuse: a single command like `python brief.py --query "..." --context context.md --urls urls.txt`, a README with the run command at the top, and a sample input so it runs out of the box. If straightforward, also expose the workflow as a Claude Code skill (SKILL.md).

Ask clarifying questions before you start.
```

---

## 7. Prompt E: voice_engine

```
Read CLAUDE.md first. Use the shared/ layer. All Claude calls go through shared/llm.py (subscription via `claude -p`, no API key).

Build a Python command-line tool that turns a research input into a 14-day LinkedIn content sequence written in a specific executive's voice, with a hard anti-slop quality gate on every output.

Context: AI-generated content is everywhere; a genuine human point of view is the only thing that converts. This tool engineers that by fingerprinting a real person's voice and rejecting generic AI writing automatically.

Inputs:
- A corpus folder of the exec's existing posts as plain .txt or .md files that I paste in. Do not scrape LinkedIn; treat the corpus folder as the ingestion point.
- A research input: a stat, finding, or short brief to build the sequence around.
- An anti-slop rules file (banned words, banned patterns, style rules) that I will populate. Read it from a config file so I can drop in my own ruleset; reuse shared/antislop.py for the gate.

Pipeline:
1. Voice fingerprint. Have Claude analyze the corpus and extract a structured voice profile saved as JSON: tone, sentence rhythm, vocabulary register, recurring arguments and themes, and an explicit "would never say" list. Save it so it can be reused without reprocessing the corpus.
2. Hook bank. Generate 10-15 opening lines for the research input, in the exec's voice.
3. Sequence generation. Produce a 14-day sequence mapped to a buyer-journey arc: early posts name a problem, middle posts share a framework or original data, later posts give proof or a founder-style narrative, ending on a soft call to action. Each post reads in the exec's voice and uses the research input.
4. Anti-slop gate. Every generated post passes through shared/antislop.py as a hard gate plus a Claude rewrite pass that strips AI tells. If a draft fails, it is rewritten, not just flagged. Keep both the pre-gate and post-gate version of each post.

Outputs: a content calendar in markdown (day, post, funnel stage), the individual posts, and a side-by-side before/after view showing the slop draft against the de-slopped final. The before/after is the key demo artifact, so make it clean and easy to read.

Package for reuse: single command, README, a small sample corpus and sample rules file so it runs out of the box. If sensible, expose the anti-slop gate as a standalone Claude Code skill.

Ask clarifying questions before you start.
```

---

## 8. Prompt F: research_engine

```
Read CLAUDE.md first. Use the shared/ layer. All Claude calls go through shared/llm.py (subscription via `claude -p`, no API key).

Build a Python command-line tool that takes a category and produces the front end of an original research report: an insight angle, a survey questionnaire, a report outline, and a set of personalized contributor invitations to target accounts.

Context: peer research reports get B2B companies into rooms with accounts who won't take a cold call, because the ask is "contribute to a report," not "take a sales call." This tool engineers that asset.

Inputs:
- A category or research theme.
- Short context on the company running the research and its ICP.
- An optional list of target contributors as name plus public URL (company page or article), pasted in by me.
- Optional reference URLs (existing reports, articles, datasets) to ground the research.

Pipeline:
1. Research synthesis. Fetch and parse any provided reference URLs (via shared/fetch.py) and have Claude synthesize them into a defensible, ideally contrarian insight angle. Use the search adapter's manual-input default; do not scrape Google.
2. Survey design. Generate a questionnaire engineered to surface one or two original, quotable statistics, with a mix of quantitative and short-answer questions.
3. Report outline. Produce a structured outline for the final report, including where the proprietary survey data slots in.
4. Contributor targeting. For each target contributor, use only the public info I provide (via shared/adapters/enrichment.py manual default) to draft a short, personalized invitation framed as contributing to peer research. Each invite references something specific about the person and makes the participation ask, not a sales ask. Pass invite prose through shared/antislop.py.

Outputs: a single markdown package containing the insight angle, the survey, the outline, and one invitation per contributor, written to an output folder. Print each stage to the console.

Be honest in the README about the boundary: real contact enrichment and email finding need paid tools like Clay or Apollo, so the targeting logic runs on public info I provide, and enrichment is the documented plug-in point.

Package for reuse: single command, README, sample inputs so it runs out of the box.

Ask clarifying questions before you start.
```

---

## 9. Smoke test (after all five are built)

- Run each tool from its single command on the included sample, then once on your real
  prospect input.
- Confirm all human-facing prose passed through the anti-slop gate (check a before/after).
- Validate generated JSON-LD in Google's Rich Results Test.
- Confirm any skipped engine (OpenAI, Perplexity, Gemini) says so in the output rather
  than failing silently.
- Confirm pipeline_engine reports thin enrichment honestly rather than inventing data.
- Run `claude /status` to confirm you stayed on the subscription throughout.

---

## 10. Loom recording plan (5 to 7 minutes)

1. Frame it in one line: five tools that map to the content-to-pipeline loop, built in
   Claude Code on a subscription, no API key.
2. Lead with `pipeline_engine`. Feed a realistic engagement CSV, show the ranked
   warm-outreach list with drafted messages, then the content attribution rollup. Say
   "this is the loop closed: content surfaced these people, here is who to reach out to
   and what to say, and here is which content is actually producing pipeline." This
   answers the revenue question first.
3. Then `entity_auditor` on a real prospect, cold. A finding in under a minute shows you
   walk in with value, not a pitch.
4. Then `brief_generator`: one query in, a brief plus a valid schema file out. Open the
   schema in the Rich Results Test to prove it is real.
5. Then `voice_engine`: show the before/after slop gate rewriting AI tells live. Your
   strongest craft moment. Mention `research_engine` briefly or skip for time.
6. Show `CLAUDE.md` and `shared/adapters/engines.py`: Claude live, other engines cleanly
   stubbed, everything on subscription. This is the system-design beat.
7. End on reusability (single commands, shared layer, skill files) and the loop framing,
   not a summary.

---

## 11. Watch-outs

- Never set `ANTHROPIC_API_KEY` in the build or demo shell. It silently switches billing
  from your subscription to the API account.
- On Pro, building and testing all five in one sitting can hit a rate limit. Space the
  runs out, or build over two sessions. Demo volume itself is trivial.
- Note for after June 15, 2026: subscription usage from `claude -p` is expected to draw
  from a separate monthly Agent SDK credit pool rather than your interactive limit.
  Still subscription, not API billing. Verify current limits before you rely on it.
- Keep the manual-input ingestion points (engagement CSV, corpus folder, contributor
  list, reference URLs) manual. If Claude Code tries to scrape LinkedIn, a CRM, or Google
  to fill them, stop it.
