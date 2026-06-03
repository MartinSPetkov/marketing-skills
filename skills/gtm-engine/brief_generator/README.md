# brief_generator

**Run command:**
```bash
python brief_generator/brief.py \
  --query "best contract testing tools" \
  --context brief_generator/samples/context.md \
  --urls brief_generator/samples/urls.txt
```

Turns a single buyer-intent query into a content brief and JSON-LD schema file designed for AI engine citation (ChatGPT, Claude, Perplexity, Gemini).

---

## What it produces

Two files written to `outputs/<query-slug>/`:

| File | Contents |
|------|----------|
| `brief.md` | Full AEO content brief: answer-first summary, H2/H3 outline, FAQ block, stats/claims with source placeholders, named entities, link suggestions, credibility signals |
| `schema.jsonld` | Valid JSON-LD in the appropriate schema type (FAQPage, Article, HowTo, or DefinedTerm) |

---

## Inputs

### Required

**`--query`** — The buyer-intent query to optimise for.
```
--query "best contract testing tools"
```

**`--context`** — Path to a text or markdown file with three things:
1. Company name (first non-empty line, optionally as a `# Heading`)
2. One-line positioning statement
3. A 2-4 sentence description of what the product does and for whom
4. Homepage URL (optional but improves entity linking)

See `samples/context.md` for the format.

### Optional

**`--urls`** — Path to a file listing competitor or reference URLs to analyse, one per line. Lines starting with `#` are ignored.

If omitted, the tool runs on Claude's current coverage of the query alone. Adding 2-5 strong competitor URLs produces a sharper gap analysis.

**`--schema`** — Override the auto-selected JSON-LD schema type.

| Value | Schema type |
|-------|-------------|
| `auto` (default) | Chosen from the recommended page type |
| `faqpage` | `FAQPage` |
| `article` | `Article` |
| `howto` | `HowTo` |
| `definedterm` | `DefinedTerm` |

Auto-selection logic:
- FAQ page → FAQPage
- Definition page → DefinedTerm
- Guide / how-to → HowTo
- Comparison → Article

---

## Pipeline

Each stage prints to the console so a screen recording shows the system working:

```
[1/4] Recon       — fetch reference URLs + query Claude for current AI coverage
[2/4] Gap analysis — compare coverage against the company's angle
[3/4] Brief assembly — produce structured brief, run answer summary through anti-slop gate
[4/4] Schema       — generate valid JSON-LD for the recommended page type
```

---

## Setup

```bash
pip install -r requirements.txt
claude login          # log in with your Claude Pro or Max subscription
claude /status        # confirm subscription is the active auth method
unset ANTHROPIC_API_KEY  # ensure no API key overrides the subscription
```

No Anthropic API key needed. See the repo-level `README.md` for full setup.

---

## Validating the schema

After running, validate the `schema.jsonld` output at:
**https://search.google.com/test/rich-results**

The tool reminds you of this after every run.

---

## What to do with the brief

1. Replace every `[SOURCE NEEDED: ...]` placeholder with a real citation.
2. Use the Answer-First Summary verbatim in the first 100 words of the page.
3. Build out each H2/H3 section following the writer notes in the outline.
4. Copy the FAQ block into your CMS and attach `schema.jsonld` to the page head.
5. Add the credibility signals listed at the bottom of the brief.

---

## Adapter note

Reference URL fetching uses `shared/fetch.py`. Google and LinkedIn URLs are blocked by design — use direct article or documentation URLs instead.

The AI engine query uses `shared/adapters/engines.py` with Claude as the active default. OpenAI, Perplexity, and Gemini are stubbed; set their respective `_API_KEY` env vars to activate them and get a multi-engine gap analysis.
