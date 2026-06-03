#!/usr/bin/env python3
"""
voice_engine: 14-day LinkedIn sequence in an executive's voice.

Usage:
    python voice_engine/voice.py \
        --corpus voice_engine/samples/corpus \
        --research voice_engine/samples/research_input.md

    python voice_engine/voice.py \
        --corpus voice_engine/samples/corpus \
        --research voice_engine/samples/research_input.md \
        --rules voice_engine/samples/antislop_rules.md \
        --reanalyze
"""

import argparse
import html as _html
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.llm import query_text, query_json
from shared.antislop import check as antislop_check
from shared import antislop as _antislop

# ── Buyer journey arc ─────────────────────────────────────────────────────────

ARC = [
    (1,  "Name the problem",                        "TOFU"),
    (2,  "Deepen the problem with data",             "TOFU"),
    (3,  "Challenge the conventional fix",           "TOFU"),
    (4,  "Show what the gap costs",                  "MOFU"),
    (5,  "Introduce a contrarian take",              "MOFU"),
    (6,  "Present original data or finding",         "MOFU"),
    (7,  "Introduce the framework (overview)",       "MOFU"),
    (8,  "Framework step 1 with specifics",          "MOFU"),
    (9,  "Framework step 2 with specifics",          "MOFU"),
    (10, "Framework step 3 with specifics",          "MOFU"),
    (11, "Proof: before/after case example",         "BOFU"),
    (12, "Proof: what the data showed",              "BOFU"),
    (13, "Founder narrative: what I learned",        "BOFU"),
    (14, "Soft CTA: here is where to start",         "BOFU"),
]


# ── Corpus loading ────────────────────────────────────────────────────────────

def load_corpus(corpus_dir: Path) -> tuple[list[str], str]:
    """Load posts from corpus dir. Returns (file_names, combined_text)."""
    paths = sorted(corpus_dir.glob("*.txt")) + sorted(corpus_dir.glob("*.md"))
    posts = []
    names = []
    for path in paths:
        text = path.read_text(encoding="utf-8").strip()
        if text:
            posts.append(f"--- {path.name} ---\n{text}")
            names.append(path.name)
    if not posts:
        raise ValueError(f"No .txt or .md files found in corpus: {corpus_dir}")
    print(f"[voice] Loaded {len(posts)} posts from corpus.")
    return names, "\n\n".join(posts)


# ── Voice fingerprinting ──────────────────────────────────────────────────────

def get_voice_profile(corpus_dir: Path, corpus_text: str, reanalyze: bool) -> dict:
    """Load cached voice profile or generate a new one from the corpus."""
    profile_path = corpus_dir / "voice_profile.json"

    if profile_path.exists() and not reanalyze:
        print(f"[voice] Loaded cached voice profile from {profile_path}")
        return json.loads(profile_path.read_text(encoding="utf-8"))

    print("[voice] Analyzing corpus to extract voice profile...")

    prompt = f"""Analyze these LinkedIn posts from an executive and extract a structured voice profile.

POSTS:
{corpus_text}

Return a JSON object with these exact keys:
- exec_name: string (infer from writing style context, or use "The Executive")
- tone: string (1-2 sentences: overall attitude, emotional register)
- sentence_rhythm: string (1-2 sentences: how sentences are built and paced)
- vocabulary_register: string (1-2 sentences: word choice, formality, jargon level)
- recurring_arguments: list of 4-6 strings (core beliefs and arguments this exec makes)
- themes: list of 4-8 strings (topics and concerns this exec returns to)
- would_never_say: list of 8-12 words or short phrases this voice would reject as inauthentic
- post_structure_patterns: string (how posts open, build, and close)
- typical_post_length: string (e.g. "150-250 words")
- sample_phrases: list of 6-10 verbatim phrases from the posts that best show the voice

Return only valid JSON. No markdown fences, no explanation."""

    profile = query_json(prompt)
    profile_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")
    print(f"[voice] Voice profile saved to {profile_path}")
    return profile


# ── Hook bank ─────────────────────────────────────────────────────────────────

def generate_hooks(profile: dict, research_input: str) -> list[str]:
    """Generate 12 opening lines in the exec's voice for the research topic."""
    print("[voice] Generating hook bank...")

    prompt = f"""You are writing opening lines for LinkedIn posts in this executive's voice.

VOICE PROFILE:
{json.dumps(profile, indent=2)}

RESEARCH INPUT:
{research_input}

Generate 12 distinct opening lines for posts about this research. Each must:
- Match the exec's sentence rhythm, vocabulary, and tone exactly
- Avoid: "Did you know", "Hot take:", "Here's why", "Let me tell you", rhetorical questions left unanswered
- Start with a number, a sharp claim, a specific observation, or a concrete scenario
- Make a reader stop scrolling without sounding like marketing copy

The exec would NEVER open with: {', '.join(profile.get('would_never_say', [])[:5])}

Return a JSON array of 12 strings. No markdown fences, no explanation."""

    result = query_json(prompt)
    hooks = result if isinstance(result, list) else list(result.values())
    print(f"[voice] Generated {len(hooks)} hooks.")
    return hooks


# ── Post generation ───────────────────────────────────────────────────────────

def generate_post(day: int, purpose: str, stage: str, profile: dict,
                  research_input: str, hook: str) -> str:
    """Draft a single LinkedIn post for the given day and purpose."""
    prompt = f"""Write a LinkedIn post for Day {day} of a 14-day content sequence.

VOICE PROFILE:
{json.dumps(profile, indent=2)}

RESEARCH INPUT:
{research_input}

SUGGESTED OPENING LINE (use it as-is or improve it while keeping the same voice):
{hook}

POST PURPOSE: {purpose}
FUNNEL STAGE: {stage} (Day {day} of 14)

Instructions:
- Write entirely in the exec's voice: match their sentence rhythm, vocabulary register, and post structure exactly.
- This post's job: {purpose.lower()}.
- Target length: {profile.get('typical_post_length', '150-250 words')}.
- The exec would never say: {', '.join(profile.get('would_never_say', []))}.
- End when the point is made. No hollow CTAs, no summary closers, no "let me know your thoughts."
- Return only the post text. No labels, no preamble."""

    return query_text(prompt)


# ── Voice-aware anti-slop gate ────────────────────────────────────────────────

def voice_clean(draft: str, profile: dict, rules_path: Path | None) -> str:
    """
    Combined anti-slop gate + voice fidelity rewrite.
    Uses antislop.check() for violation detection, then rewrites in one pass
    that both removes slop and preserves the exec's voice.
    """
    violations = antislop_check(draft)

    if rules_path and rules_path.exists():
        rules = rules_path.read_text(encoding="utf-8")
    else:
        rules = _antislop._BUILT_IN_RULES_SUMMARY

    violation_block = ""
    if violations:
        items = "\n".join(f"- {v}" for v in violations)
        violation_block = f"\n\nSpecific violations to fix:\n{items}"

    prompt = f"""Rewrite this LinkedIn post to remove AI-style writing while preserving the executive's voice exactly.

STYLE RULES (apply all):
{rules}
{violation_block}

VOICE TO PRESERVE:
{json.dumps(profile, indent=2)}

The rewrite must:
- Fix every violation listed above
- Sound like this executive wrote it, not like cleaned-up AI output
- Keep the same argument and evidence from the draft
- Match their sentence rhythm, vocabulary register, and post structure
- End when the point is made

Return only the rewritten post. No preamble, no explanation, no labels.

DRAFT TO REWRITE:
{draft}"""

    return query_text(prompt).strip()


# ── Sequence generation ───────────────────────────────────────────────────────

def generate_sequence(profile: dict, research_input: str, hooks: list[str],
                      rules_path: Path | None, out_posts_dir: Path) -> list[dict]:
    """Generate all 14 posts with before/after anti-slop pairs."""
    posts = []

    for i, (day, purpose, stage) in enumerate(ARC):
        print(f"[voice] Day {day:02d}/{len(ARC)}  {stage}  {purpose}...")

        hook = hooks[i % len(hooks)] if hooks else ""
        draft = generate_post(day, purpose, stage, profile, research_input, hook)

        violations = antislop_check(draft)
        label = f"{len(violations)} violation(s)" if violations else "clean draft"
        print(f"           {label} — rewriting in voice...")

        final = voice_clean(draft, profile, rules_path)

        posts.append({
            "day": day,
            "purpose": purpose,
            "stage": stage,
            "draft": draft,
            "violations": violations,
            "final": final,
        })

        (out_posts_dir / f"day_{day:02d}.md").write_text(
            f"# Day {day}: {purpose} ({stage})\n\n{final}\n",
            encoding="utf-8",
        )

    return posts


# ── Output writers ────────────────────────────────────────────────────────────

def write_calendar(posts: list[dict], out_dir: Path) -> None:
    lines = [
        "# 14-Day LinkedIn Content Calendar\n",
        "| Day | Stage | Purpose | Opening |",
        "| --- | ----- | ------- | ------- |",
    ]
    for p in posts:
        opening = p["final"].splitlines()[0][:80].replace("|", "/")
        lines.append(f"| {p['day']} | {p['stage']} | {p['purpose']} | {opening}… |")

    path = out_dir / "calendar.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[voice] Calendar  → {path}")


def write_before_after_html(posts: list[dict], profile: dict, out_dir: Path) -> None:
    exec_name = profile.get("exec_name", "Executive")

    cards = []
    for p in posts:
        stage_cls = p["stage"].lower()
        draft_text = _html.escape(p["draft"])
        final_text = _html.escape(p["final"])

        viol_html = ""
        if p["violations"]:
            items = "".join(f"<li>{_html.escape(v)}</li>" for v in p["violations"])
            viol_html = (
                f'<div class="violations">'
                f'<strong>{len(p["violations"])} violation(s) found and fixed:</strong>'
                f"<ul>{items}</ul></div>"
            )

        cards.append(f"""
<div class="card">
  <div class="card-header">
    <span class="badge day">Day {p['day']}</span>
    <span class="badge stage {stage_cls}">{p['stage']}</span>
    <span class="purpose">{_html.escape(p['purpose'])}</span>
  </div>
  <div class="cols">
    <div class="col before">
      <div class="col-label">Before &mdash; draft</div>
      {viol_html}
      <pre class="post">{draft_text}</pre>
    </div>
    <div class="col after">
      <div class="col-label">After &mdash; de-slopped</div>
      <pre class="post">{final_text}</pre>
    </div>
  </div>
</div>""")

    cards_html = "\n".join(cards)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Voice Engine &mdash; Before / After &mdash; {_html.escape(exec_name)}</title>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 15px;
  line-height: 1.65;
  color: #1a1a1a;
  background: #f4f4f0;
  padding: 2rem 1rem;
}}

.page {{ max-width: 1120px; margin: 0 auto; }}

header {{
  background: #1a1a2e;
  color: #fff;
  padding: 1.75rem 2rem;
  border-radius: 6px 6px 0 0;
}}

header h1 {{ font-size: 1.4rem; font-weight: 700; letter-spacing: -.02em; }}
header p {{ margin-top: .4rem; color: #9ab; font-size: .88rem; }}

.card {{
  background: #fff;
  border-bottom: 2px solid #e8e8e4;
  padding: 1.5rem 2rem;
}}

.card:last-of-type {{
  border-bottom: none;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 2px 6px rgba(0,0,0,.07);
}}

.card-header {{
  display: flex;
  align-items: center;
  gap: .6rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}}

.badge {{
  font-size: .72rem;
  font-weight: 700;
  padding: .2rem .55rem;
  border-radius: 3px;
  letter-spacing: .04em;
  text-transform: uppercase;
}}

.badge.day {{ background: #f0f0ec; color: #555; }}
.badge.tofu {{ background: #dbeafe; color: #1e40af; }}
.badge.mofu {{ background: #fef3c7; color: #92400e; }}
.badge.bofu {{ background: #d1fae5; color: #065f46; }}

.purpose {{ font-size: .88rem; color: #444; }}

.cols {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.2rem;
}}

@media (max-width: 720px) {{ .cols {{ grid-template-columns: 1fr; }} }}

.col {{
  border-radius: 4px;
  padding: 1rem 1.1rem;
}}

.col.before {{ background: #fff8f8; border: 1px solid #f0cece; }}
.col.after  {{ background: #f4fff6; border: 1px solid #b8e4c4; }}

.col-label {{
  font-size: .7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  margin-bottom: .65rem;
}}

.col.before .col-label {{ color: #b83030; }}
.col.after  .col-label {{ color: #1e7a3c; }}

.violations {{
  background: #fff0f0;
  border-left: 3px solid #d04040;
  padding: .5rem .75rem;
  margin-bottom: .75rem;
  font-size: .78rem;
  border-radius: 0 3px 3px 0;
}}

.violations strong {{ color: #b83030; }}
.violations ul {{ padding-left: 1rem; margin-top: .2rem; }}
.violations li {{ margin: .12rem 0; }}

pre.post {{
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  font-size: .875rem;
  line-height: 1.7;
}}

footer {{
  text-align: center;
  font-size: .78rem;
  color: #aaa;
  padding: 1.25rem;
}}
</style>
</head>
<body>
<div class="page">

<header>
  <h1>Voice Engine &mdash; Before / After</h1>
  <p>Executive: {_html.escape(exec_name)} &mdash; 14-day LinkedIn sequence &mdash; anti-slop gate applied to every post</p>
</header>

{cards_html}

<footer>Generated by gtm-engine voice_engine &mdash; open this file in any browser, no server needed.</footer>
</div>
</body>
</html>"""

    path = out_dir / "before_after.html"
    path.write_text(html, encoding="utf-8")
    print(f"[voice] Before/after → {path}")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a 14-day LinkedIn sequence in an executive's voice.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--corpus", required=True,
        help="Folder of exec's LinkedIn posts as .txt or .md files",
    )
    parser.add_argument(
        "--research", required=True,
        help="Research input file (.md or .txt) with the finding or brief",
    )
    parser.add_argument(
        "--rules", default=None,
        help="Anti-slop rules file (optional; defaults to built-in rules)",
    )
    parser.add_argument(
        "--reanalyze", action="store_true",
        help="Re-analyze corpus even if a cached voice_profile.json exists",
    )
    args = parser.parse_args()

    corpus_dir = Path(args.corpus)
    if not corpus_dir.is_dir():
        print(f"Error: corpus directory not found: {corpus_dir}", file=sys.stderr)
        sys.exit(1)

    research_path = Path(args.research)
    if not research_path.exists():
        print(f"Error: research input file not found: {research_path}", file=sys.stderr)
        sys.exit(1)

    rules_path = Path(args.rules) if args.rules else None

    research_input = research_path.read_text(encoding="utf-8").strip()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("outputs") / f"voice_{timestamp}"
    out_posts_dir = out_dir / "posts"
    out_posts_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[voice] Output: {out_dir}\n")

    # Stage 1: voice fingerprint
    _, corpus_text = load_corpus(corpus_dir)
    profile = get_voice_profile(corpus_dir, corpus_text, args.reanalyze)

    exec_name = profile.get("exec_name", "Unknown Exec")
    print(f"[voice] Exec:  {exec_name}")
    print(f"[voice] Tone:  {profile.get('tone', '')}\n")

    # Stage 2: hook bank
    hooks = generate_hooks(profile, research_input)
    hooks_path = out_dir / "hooks.md"
    hooks_path.write_text(
        "# Hook Bank\n\n" + "\n\n".join(f"{i + 1}. {h}" for i, h in enumerate(hooks)) + "\n",
        encoding="utf-8",
    )
    print(f"[voice] Hooks     → {hooks_path}\n")

    # Stage 3 + 4: sequence + anti-slop gate
    print(f"[voice] Generating 14-day sequence for {exec_name}...\n")
    posts = generate_sequence(profile, research_input, hooks, rules_path, out_posts_dir)

    # Save voice profile copy in output dir
    (out_dir / "voice_profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")

    # Stage 5: write outputs
    print()
    write_calendar(posts, out_dir)
    write_before_after_html(posts, profile, out_dir)

    print(f"\n[voice] Done.")
    print(f"  Calendar:     {out_dir}/calendar.md")
    print(f"  Posts:        {out_dir}/posts/  (day_01.md … day_14.md)")
    print(f"  Before/after: {out_dir}/before_after.html")
    print(f"  Hooks:        {out_dir}/hooks.md")
    print(f"  Profile:      {out_dir}/voice_profile.json  (cached in corpus too)")


if __name__ == "__main__":
    main()
