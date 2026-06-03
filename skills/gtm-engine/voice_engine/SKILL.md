# SKILL: antislop-gate

Run the anti-slop gate on any human-facing prose. Detects AI-style writing violations and rewrites via Claude.

## When to invoke

Use this skill when the user wants to:
- Clean up marketing copy, blog posts, LinkedIn posts, email sequences, or any human-facing text
- Check whether text passes the anti-slop rules before publishing
- Strip AI tells ("leverage", "seamless", "it's important to note…") from a draft
- Apply a custom ruleset from a file to a piece of writing
- Understand what specific violations are in a draft without rewriting it

## What you need from the user

Before running, confirm you have:

1. **Text to clean** — paste inline, or provide a file path
2. **Rules file** (optional) — path to a `.md` rules file; defaults to built-in rules in `shared/antislop.py`

## How to run

### Check for violations only (no rewrite):

```bash
python -c "
import sys
sys.path.insert(0, '.')
from shared.antislop import check
text = open('path/to/draft.txt').read()
violations = check(text)
if violations:
    print(f'{len(violations)} violation(s):')
    for v in violations: print(' -', v)
else:
    print('No violations found.')
"
```

### Clean and rewrite (built-in rules):

```bash
python -c "
import sys
sys.path.insert(0, '.')
from shared.antislop import clean
text = open('path/to/draft.txt').read()
print(clean(text))
"
```

### Clean with a custom rules file:

```bash
python -c "
import sys
sys.path.insert(0, '.')
from shared.antislop import clean
text = open('path/to/draft.txt').read()
print(clean(text, rules_path='antislop_rules.md'))
"
```

### Clean text the user pastes inline:

```bash
python -c "
import sys
sys.path.insert(0, '.')
from shared.antislop import clean
text = '''PASTE TEXT HERE'''
print(clean(text))
"
```

## What the gate does

Two steps on every call to `clean()`:

1. **Rule scan** — detects banned words (delve, leverage, robust, synergy…), banned phrases ("it's important to note", "let's dive into"…), em dashes, and hollow intensifiers.

2. **Claude rewrite** — always runs, regardless of whether violations were found. Strips AI tells and enforces style rules: short declarative sentences, active voice, evidence first, no filler openers or summary closers.

The gate is hard: failed text is rewritten, not just flagged. `check()` is available separately when you only want the violation list.

## Rules file format

The rules file is plain Markdown. The gate passes its full content to Claude as the style guide. Sections it recognises well:

```markdown
## Hard rules
- No em dashes.
- Short declarative sentences.
…

## Banned words
word1, word2, word3…

## Banned phrases
"phrase one", "phrase two"…
```

See `antislop_rules.md` (repo root) or `voice_engine/samples/antislop_rules.md` for working examples.

## After running

- Show the user the cleaned text.
- If violations were found, briefly list them so the user can see what was removed.
- If they want a before/after comparison for a full post sequence, point them to `voice_engine/voice.py` — it runs the gate on every post and produces `before_after.html`.

## API reference

```python
from shared.antislop import clean, check

# Rewrite and return cleaned text
cleaned = clean(text)
cleaned = clean(text, rules_path="path/to/rules.md")

# List violations without rewriting
violations: list[str] = check(text)
violations = check(text, rules_path="path/to/rules.md")
```
