# voice_engine

Turns a research finding into a 14-day LinkedIn sequence in a specific executive's voice, with a hard anti-slop gate on every post.

```bash
python voice_engine/voice.py \
  --corpus voice_engine/samples/corpus \
  --research voice_engine/samples/research_input.md
```

Run from the repo root. Outputs go to `outputs/voice_<timestamp>/`.

---

## What it does

AI-generated content is everywhere. A genuine human point of view is the only thing that converts. This tool engineers that by fingerprinting a real person's voice and rejecting generic AI writing automatically.

**Pipeline:**

1. **Voice fingerprint** — Claude analyzes the exec's post corpus and extracts a structured JSON profile: tone, sentence rhythm, vocabulary register, recurring arguments, themes, and an explicit "would never say" list. The profile is cached so you can iterate without reprocessing.

2. **Hook bank** — 12 opening lines for the research finding, written in the exec's voice. Saved to `hooks.md` so you can mix and match.

3. **Sequence generation** — 14 posts mapped to a buyer-journey arc:
   - Days 1–3: name and deepen the problem (TOFU)
   - Days 4–10: contrarian takes, data, framework (MOFU)
   - Days 11–14: proof, founder narrative, soft CTA (BOFU)

4. **Anti-slop gate** — Every draft goes through `shared/antislop.py` to detect violations, then a voice-aware Claude rewrite that removes AI tells while keeping the exec's fingerprint. Both the pre-gate draft and the final post are kept.

**Outputs:**

| File | What it is |
| ---- | ---------- |
| `before_after.html` | Side-by-side comparison of every draft vs. final — the key demo artifact |
| `calendar.md` | Day / stage / purpose / opening line for the full sequence |
| `posts/day_01.md` … `posts/day_14.md` | Individual final posts, ready to copy-paste |
| `hooks.md` | The hook bank (12 opening lines) |
| `voice_profile.json` | The extracted voice profile (also cached in corpus dir) |

---

## Inputs

### Corpus (required)

A folder of the exec's existing posts as `.txt` or `.md` files. Paste them in — one post per file. Do not scrape LinkedIn.

The tool needs at least 5 posts to produce a useful fingerprint. 10–15 posts is ideal.

```
voice_engine/samples/corpus/
├── post_01.txt
├── post_02.txt
…
```

A cached `voice_profile.json` is written to the corpus folder after the first run. Subsequent runs skip the analysis step unless you pass `--reanalyze`.

### Research input (required)

A short `.md` or `.txt` file with the finding or brief to build the sequence around. Can be a single stat, a data point, or a few sentences of context.

See `voice_engine/samples/research_input.md` for the format.

### Anti-slop rules (optional)

A rules file in the format of `antislop_rules.md`. If omitted, the built-in rules in `shared/antislop.py` apply.

```bash
python voice_engine/voice.py \
  --corpus my_corpus/ \
  --research my_finding.md \
  --rules antislop_rules.md   # repo-root rules file
```

---

## All flags

| Flag | Required | Description |
| ---- | -------- | ----------- |
| `--corpus` | Yes | Path to folder of exec's posts |
| `--research` | Yes | Path to research input file |
| `--rules` | No | Path to anti-slop rules file |
| `--reanalyze` | No | Ignore cached voice profile and re-analyze corpus |

---

## Sample run

The sample corpus is a fictional B2B exec (Alex Moreau) whose posts focus on demand gen, content strategy, and AI search visibility. The sample research input is a set of invented statistics on the same topic.

```bash
# First run: analyzes corpus, caches profile
python voice_engine/voice.py \
  --corpus voice_engine/samples/corpus \
  --research voice_engine/samples/research_input.md \
  --rules voice_engine/samples/antislop_rules.md

# Subsequent runs: loads cached profile (fast)
python voice_engine/voice.py \
  --corpus voice_engine/samples/corpus \
  --research voice_engine/samples/research_input.md

# Force re-analysis (e.g. after adding posts to corpus)
python voice_engine/voice.py \
  --corpus voice_engine/samples/corpus \
  --research voice_engine/samples/research_input.md \
  --reanalyze
```

Open `outputs/voice_<timestamp>/before_after.html` in any browser to see the before/after comparison.

---

## Using your own exec

1. Create a corpus folder and drop in 10+ of their posts as `.txt` or `.md` files.
2. Write a short research input file with your finding.
3. Run the tool. Review the voice profile JSON — correct anything that looks wrong.
4. If the profile needs adjusting, edit `voice_profile.json` in the corpus folder directly and re-run (the edits persist because the cache is loaded unless `--reanalyze` is passed).

---

## Notes

- The `ANTHROPIC_API_KEY` must NOT be set in your environment. This repo authenticates through your Claude subscription via `claude -p`. See repo-root README for setup.
- A full 14-post sequence requires roughly 30 Claude calls (post generation + anti-slop rewrites). On Claude Pro, spacing out the run or using Max is recommended.
- Posts are approximately 150–280 words. LinkedIn's limit is ~3,000 characters; no post will approach that.
- The sample research figures are invented. Replace them with real data before publishing.
