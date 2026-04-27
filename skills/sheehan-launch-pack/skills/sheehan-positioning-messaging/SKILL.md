---
name: sheehan-positioning-messaging
description: Build a positioning statement and messaging house for a launch using Mary Sheehan's framework from The Pocket Guide to Product Launches. Use whenever a user says "write me a positioning statement," "build a messaging house," "what's our value proposition," "what are our key messages," "we don't have positioning," "run a messaging workshop," "competitive positioning," "differentiators," "proof points," "messaging hierarchy," "how do we talk about this product," or any request about shaping the external story of a product or feature. Apply this skill AFTER the target market is defined, because positioning without a known audience is guessing. Do NOT use this skill for brand identity, visual design, or overall company narrative; this skill is about product-level positioning for a specific launch.
---

# Sheehan Positioning and Messaging

Positioning is the strategic decision about who the product is for and what makes it different. Messaging is how that decision shows up in every piece of copy. Get positioning wrong and every headline, ad, and pitch has to work harder than it should.

## When to use this skill

Trigger on:

- "Write a positioning statement."
- "Build a messaging house."
- "What's our value prop?"
- "Help me run a messaging workshop."
- "Our messaging feels off."
- "How do we differentiate from [competitor]?"
- "I need proof points."
- "Give me the headline, subhead, and bullets for the launch page."

Prerequisites: target market defined (see `sheehan-target-market`). GTM plan in progress or drafted (see `sheehan-gtm-plan`). Without a target, positioning is fiction.

## The positioning statement

Sheehan's template, adapted from Geoffrey Moore:

> For **[target customer]**
> who **[statement of need or opportunity]**,
> **[product name]** is a **[product category]**
> that **[key benefit, compelling reason to buy]**.
> Unlike **[primary competitive alternative]**,
> our product **[primary differentiation]**.

Fill it in with real answers, not placeholders. Each blank is a forcing function:

- **Target customer:** specific role, company type. "Small business owners" is wrong. "Bakery owners in Northern California with under 10 employees" is right.
- **Statement of need:** the job to be done, from the JTBD research. Use their words.
- **Product name.**
- **Product category:** the mental bucket they'll file you in. Picking the wrong category is a common launch mistake.
- **Key benefit:** the one thing that matters most. Not a feature list.
- **Primary competitor:** the actual alternative, which is often "doing nothing" or "spreadsheets," not the competitor your CEO worries about.
- **Primary differentiation:** the unique, defensible thing.

The statement is an internal artifact. Nobody outside the company should ever read it verbatim. Its job is to align the team on the strategic choices. External copy is written from it, not as it.

## The messaging house

One page. Three levels.

### Top floor: the tagline or one-liner

The external-facing short statement. 5-10 words. Sits on the homepage hero.

Examples:

- "The customer data platform for marketers."
- "Meetings that end with clear next steps."

### Middle floor: three pillars

Three top-level messages. Each pillar is a single idea that matters to the target customer, expressed in their words.

For each pillar:

- **Headline:** 3-7 words. The idea in compressed form.
- **Subhead:** 1-2 sentences. What the pillar means concretely.
- **Proof points:** 3-5 bullets. Features, customer quotes, data points, comparisons.

Three pillars is the default because three fits in a deck, a website section, and a pitch. Two pillars is fine if the story is tight. Four is the ceiling.

### Ground floor: supporting content

Per-audience variants, channel-specific versions, and secondary messages. For each persona, write:

- Persona-specific headline.
- Persona-specific pain point language.
- Persona-specific proof.

See `references/messaging-house-template.md` for the full structure.

## Step 1: Run the messaging workshop

Before writing, gather inputs. Sheehan's workshop is 90 minutes, 4-8 people: PMM, PM, Sales lead, CS lead, and an exec (usually CMO or CEO).

Agenda:

1. Review target market and personas (10 min).
2. Review competitive alternatives (10 min).
3. Brainstorm: what's the one thing that matters most to the customer? (20 min, silent then share).
4. Pressure-test: is this true, and is it different? (20 min).
5. Draft positioning statement together (20 min).
6. Assign who writes the messaging house draft (10 min).

See `references/messaging-workshop-agenda.md` for the full agenda and questionnaire.

## Step 2: Write the positioning statement

PMM writes the draft within 48 hours of the workshop. Share with workshop attendees for comments. Final version signed off by the exec sponsor (usually CMO or CEO).

Rules:

- No more than 3 drafts. If you're on draft 5, the problem is the underlying strategy, not the wording.
- Read it out loud. Stumble means rewrite.
- No jargon. A customer should understand every word.
- Test it against a competitor's statement. Are you different, or the same with a different logo?

## Step 3: Write the messaging house

Work top-down: tagline, then pillars, then supporting content.

For each pillar:

1. Start with the customer's pain point, in their words.
2. Write the benefit that fixes it.
3. List the proof: features, data, quotes.
4. Compress to a headline and subhead.

Rules:

- Use customer words verbatim where possible (from JTBD interview quotes).
- Every claim has proof. A bold statement without evidence is empty.
- Parallel structure across pillars. If pillar 1 starts with a verb, all three do.
- No synonyms of the same thing. If two pillars mean the same thing, collapse them.

## Step 4: Build the competitive matrix

A 2-axis table: features or dimensions (rows) versus competitors (columns). See `references/competitive-matrix.md`.

Purpose:

- Force honesty about where you win and lose.
- Give sales the ammo for competitive deals.
- Find the defensible differentiation.

Don't publish this externally. It's an internal artifact. The external "vs. competitor" page uses a subset of the honest comparison.

## Step 5: Write external copy from the messaging house

Every piece of launch copy draws from the house:

- Homepage hero: tagline + pillar 1 subhead.
- Launch blog post: tagline + 3 pillars + proof.
- Press release: positioning statement, softened; 2-3 pillars; customer quote.
- Sales deck: tagline; 3 pillars as 3 slides; proof per slide.
- One-sheet: tagline; 3 pillars; pricing; CTA.
- Email: single pillar + one proof point + CTA.

If a piece of copy doesn't trace back to the house, ask why. Either it's off-message or the house needs a row it's missing.

## Step 6: Test before shipping

Three tests:

1. **Customer test.** Show it to 3-5 target customers. Do they understand it without explanation? Would they click it?
2. **Differentiation test.** Show the competitor's website next to yours. Are you actually different, or is it the same promise in different fonts?
3. **Sales test.** Can a sales rep deliver the pitch from memory after training? If not, it's too long or too abstract.

If any test fails, go back to the pillar, not the copy.

## Output format

When asked to build positioning and messaging, produce:

```
# Positioning and messaging: [Product / launch]

## Positioning statement
For [target customer] who [need], [product name] is a [category]
that [key benefit]. Unlike [competitor], our product [differentiation].

## Messaging house

### Tagline
[5-10 word external statement]

### Pillar 1: [Headline, 3-7 words]
Subhead: [1-2 sentences]
Proof:
- [Point]
- [Point]
- [Point]

### Pillar 2: [Headline]
Subhead: [...]
Proof: [...]

### Pillar 3: [Headline]
Subhead: [...]
Proof: [...]

## Persona variants
### For [Persona A]
- Headline: ...
- Pain point language: ...
- Proof: ...

### For [Persona B]
- ...

## Competitive matrix
[Link or embed]

## Notes and watch-outs
[Things to avoid, known objections, language that backfired in testing]
```

## What to avoid

- Never write positioning before the target market is defined. Everything downstream inherits the vagueness.
- Never ship the positioning statement as external copy. It's an internal artifact.
- Never have more than 4 pillars. More and no one can recall them.
- Never use the competitor's language in your own positioning. If you sound like them, you are them.
- Never claim a differentiator that doesn't hold up against an honest competitive review.
- Never skip the customer test. Messaging that tests well internally often fails externally.

## References

- `references/messaging-house-template.md` - the full one-page messaging house structure.
- `references/messaging-workshop-agenda.md` - 90-minute workshop with questions.
- `references/competitive-matrix.md` - how to build and use the internal competitive matrix.
- `references/positioning-statement-examples.md` - 5 filled-out positioning statements across industries.

## Examples

- `examples/messaging-house-b2b-saas.md` - full messaging house for a product analytics launch.
- `examples/messaging-house-consumer.md` - full messaging house for a consumer mobile app.
