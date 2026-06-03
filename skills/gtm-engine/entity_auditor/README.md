# entity_auditor

Audits a brand's entity authority and generates the assets to fix it.

Entity authority is how recognizable a brand is to AI engines as a distinct, well-defined
entity. This is different from a page-level SEO audit. AI engines cite brands they can
independently verify — this tool measures that signal and tells you what to fix.

## Run

```
python entity_auditor/entity_audit.py --brand "Acme" --url "https://acme.com"
```

With an explicit about page:

```
python entity_auditor/entity_audit.py --brand "Acme" --url "https://acme.com" --about-url "https://acme.com/about"
```

Run from the repo root. Authenticate first:

```
claude login
claude /status   # confirm subscription is the active auth method
unset ANTHROPIC_API_KEY
```

## What it does

**Five pipeline stages, printed to the console as they run:**

1. **On-site signals** — fetches the homepage and about page (auto-discovered from nav
   if not specified). Extracts existing JSON-LD, checks for Organization schema and
   sameAs links, and captures social profiles.

2. **Wikidata lookup** — queries the free public Wikidata API to check whether the brand
   has an entity entry and what it says.

3. **Scoring** — Claude scores four dimensions (0–10 each) and gives a letter grade (A–F):
   - Entity Presence: is the brand findable as a named entity?
   - Description Consistency: does it describe itself the same way everywhere?
   - Structured Data: is the Organization schema complete?
   - Third-Party Corroboration: how many independent sources name it?

4. **Fix assets** — generates three deliverables:
   - A valid `Organization` JSON-LD block with sameAs links
   - A one-paragraph entity description for Wikidata and directory reuse
   - A prioritized list of 10 authoritative directories to claim

5. **Report** — writes a self-contained HTML report and the JSON-LD as its own file.

## Outputs

Written to `outputs/<brand-slug>/`:

| File | Contents |
|---|---|
| `report.html` | Full audit: scores, gap analysis, all three fix assets |
| `organization.jsonld` | Ready-to-paste Organization schema |

Open `report.html` in any browser — no server needed.

**After running:** validate `organization.jsonld` at
[Google Rich Results Test](https://search.google.com/test/rich-results).

## Adapters and cost

- Claude (subscription, no API key): scoring, asset generation, anti-slop rewrites
- Wikidata (free public API, no key): entity presence check
- No other paid services used

Everything runs cold on any public B2B SaaS URL. Target runtime: under 60 seconds.

## Honesty

The tool never fabricates facts. If a field cannot be verified, it uses a bracketed
placeholder (e.g. `[CRUNCHBASE_URL]`). Replace placeholders before publishing.

## Adding more off-site sources

Each external check lives in `sources/`. To add a new source:
1. Create `entity_auditor/sources/<source_name>.py`
2. Implement a `lookup(brand_name, homepage_url) -> YourResult` function
3. Import and call it in `entity_audit.py` between stages 2 and 3
