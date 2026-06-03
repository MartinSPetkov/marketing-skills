# SKILL: brief-generator

Generate an AEO content brief and JSON-LD schema for a buyer-intent query.

## When to invoke

Use this skill when the user wants to:
- Create a content brief optimised for AI engine citation
- Generate schema markup (FAQPage, HowTo, Article, DefinedTerm) for a page
- Understand what gaps exist between their content angle and current AI coverage
- Produce an answer-first summary block an AI engine can cite verbatim

## What you need from the user

Before running, confirm you have:

1. **Target query** — the exact buyer-intent phrase (e.g. "best contract testing tools")
2. **Company context** — one of:
   - A path to an existing context file (`--context path/to/context.md`)
   - Inline: company name, one-line positioning, 2-4 sentence description, homepage URL
3. **Reference URLs** (optional) — 2-5 competitor or reference page URLs the user wants analysed

If the user provides context inline, write it to `brief_generator/samples/context.md` (or a new file) before running.

## How to run

```bash
# With reference URLs
python brief_generator/brief.py \
  --query "<query>" \
  --context <path-to-context.md> \
  --urls <path-to-urls.txt>

# Without reference URLs (AI coverage only)
python brief_generator/brief.py \
  --query "<query>" \
  --context <path-to-context.md>

# Force a specific schema type
python brief_generator/brief.py \
  --query "<query>" \
  --context <path-to-context.md> \
  --schema faqpage
```

Run from the repo root. Outputs go to `outputs/<query-slug>/`.

## What it produces

- `outputs/<slug>/brief.md` — complete AEO brief with outline, FAQ, entities, links, credibility signals
- `outputs/<slug>/schema.jsonld` — valid JSON-LD ready to paste into the page head

## After running

- Show the user the path to both output files.
- Remind them to replace `[SOURCE NEEDED: ...]` placeholders with real citations before publishing.
- Remind them to validate the schema at https://search.google.com/test/rich-results

## Sample run (for testing)

```bash
python brief_generator/brief.py \
  --query "best contract testing tools" \
  --context brief_generator/samples/context.md \
  --urls brief_generator/samples/urls.txt
```
