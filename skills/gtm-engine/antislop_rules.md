# Anti-slop rules

The quality gate for voice_engine and any prose tool. Failed text is rewritten, not just
flagged.

## Hard rules
- No em dashes. Use commas, periods, colons, or semicolons.
- Short declarative sentences. Subject and verb first, then qualifications.
- Active voice by default.
- Vary sentence length. Short sentences land hard.
- Concrete and specific. Name the thing. Skip the abstraction.
- No filler openers and no summary closers. Start with the point. End when it is made.
- State claims directly. No fence-sitting.
- Cut qualifiers: very, really, quite, rather, somewhat.

## The four-question filter (run on every sentence)
1. Can I delete this word without losing meaning? Delete it.
2. Is this the simplest way to say it? Simplify.
3. Would I say this out loud to a colleague? If not, rewrite.
4. Does this add information or just sound impressive? If the latter, cut it.

## Banned words (delete on sight, replace with the plain word)
delve, moreover, furthermore, albeit, indeed, utilize, leverage, facilitate, robust,
seamless, comprehensive, cutting-edge, holistic, synergy, paradigm, innovative,
transformative, empower, realm, tapestry, landscape (metaphorical), multifaceted,
nuanced, underscore, testament, myriad, plethora, illuminate, foster, cultivate,
spearhead, bolster, pivotal, embark, navigate (metaphorical), stakeholder, bandwidth,
actionable, ecosystem, craft (verb), curate, resonate, streamline, elevate, harness,
unlock, tailor, journey, compelling, powerful, impactful, crucial, significant, ensure,
optimal, drives (results), enables, aligned with, key (adjective), space (as in "the AI
space"), stands out, double down, deep dive, circle back, unpack, shed light on, pave
the way, set the stage, raise the bar, move the needle.

## Banned phrases

Throat-clearing (delete, start with the point):
"It's important to note that", "It's worth mentioning that", "It goes without saying",
"In today's X landscape", "Let's dive into", "Without further ado", "In this article we
will", "As we all know", "Let's break it down", "Let's unpack this".

Empty hedges (say it or do not):
"To be fair", "To be honest", "At the end of the day", "When it comes to", "In terms of",
"It's crucial to", "It's no secret that", "It's clear that", "Needless to say".

Fake-casual honesty markers (they imply the rest was not honest):
"And honestly", "Honestly", "I'll be honest", "If I'm being honest", "Candidly",
"Frankly", "Real talk", "The truth is", "I won't sugarcoat it".

## Exclude
- Academic hedging: "it could be argued", "one might suggest", "research suggests" with
  no named source.
- Motivational poster language: "believe in yourself", "unlock your potential".
- Corporate positivity: "exciting opportunity", "best practice", "value-add".
- Summary paragraphs that recap what was just said.
- Rhetorical questions left unanswered.
