---
name: sheehan-target-market
description: Define and research a launch's target market using Mary Sheehan's framework from The Pocket Guide to Product Launches. Use whenever a user says "who is this product for," "define my target audience," "build a persona for a launch," "plan customer interviews," "talk to customers before we launch," "Jobs to Be Done interviews," "run a quick survey on our customers," "segment our users," "I keep hearing 'it's for everyone,'" or any request that involves figuring out who a launch is targeting and how to verify it. Apply this skill EARLY in launch planning, before positioning, messaging, or the channel plan, because every downstream choice depends on knowing the customer. Do NOT use this skill for deep academic UX research or statistically rigorous market sizing; this skill is scrappy, launch-focused, and aimed at product marketers running a launch in weeks, not quarters.
---

# Sheehan Target Market

Define who a launch is for, and prove it with direct customer contact. "It's for everyone" means it's for no one. The product marketer's job is to force specificity, then go talk to real people.

## When to use this skill

Trigger on:

- "Who is this product for?"
- "Build a persona for our launch."
- "We need to do customer research before we launch."
- "Help me set up customer interviews."
- "I want to run a Jobs to Be Done study."
- "How do I segment our customers for this launch?"
- "We're being told the product is for everyone. Help."

Use this skill BEFORE positioning, messaging, goals, or channels are locked. If positioning has already been done without a defined target, stop and do this first; everything downstream inherits the ambiguity.

## The "it's for everyone" problem

When the PM, founder, or eng lead insists the product is "for everyone," push back. Saying "everyone" really means:

- You haven't talked to a prospective customer.
- You don't know how anyone would use the product.
- You can't estimate market size (TAM).
- You can't name channels to reach them.

Without a defined target, there's no way to test product/market fit. Marc Andreessen: "The number one company killer is lack of market."

Ask the dumb question: who is this product for? Keep asking until you get a specific persona with demographics, role, behavior, and motivation.

## Step 1: Write a starting hypothesis

If no customer data exists, write a starting hypothesis. Be as specific as possible. Bad: "small businesses." Good: "Northern California bakery owners, under 10 employees, who run promotions on Instagram but don't have a loyalty program." The specificity is the point. You'll revise after research.

Fill in:

- **Role and level:** e.g. "Head of Product at Series B-D B2B SaaS companies."
- **Company type:** size, industry, maturity.
- **Geography:** region, country, time zone.
- **Behavior today:** what tools and habits they use.
- **Motivation:** the job they're trying to get done.
- **Who this is NOT for:** explicitly exclude segments.

## Step 2: Pick a research tactic

Sheehan's six tactics, ranked by speed:

1. **Email surveys.** Fastest. Use TypeForm or Google Forms. Segment your list by current/churned/prospect.
2. **Phone interviews.** 30 minutes with at least 5 people. Under 5 and one loud voice distorts the sample. Use Calendly for scheduling and Dialpad or Zoom for recording (get consent).
3. **iPad at a conference or virtual booth.** Target audience in one room. Offer a small incentive.
4. **LinkedIn messages.** Good for recruiting participants when you don't have a list. Test headlines.
5. **Recruitment tools like Vancery.** Pricey ($100+ per respondent) but fast and well-targeted.
6. **Incentivize.** $5-$10 gift cards for surveys; $50 for interviews; a raffle ($250-$500) for bigger studies.

Recommend the tactic based on timeline and data available:

- Less than 2 weeks and no list? LinkedIn outreach + Vancery.
- 2-4 weeks with a customer list? Email survey + 5-10 phone interviews.
- More than a month and a real research budget? 20-30 interviews using the Jobs to Be Done script.

## Step 3: Run the interviews (Jobs to Be Done script)

If the user picks interviews, walk them through the JTBD-based script in `references/jtbd-script.md`. Key rules:

- Same script for everyone. Comparability matters more than conversation flow.
- Record with consent (illegal without consent in California and other two-party-consent states).
- Listen personally to at least a handful of recordings. Note exact words, hesitations, excitements, frustrations. These become messaging later.
- If you delegate interviews, train the team on the script and have them record.

Target 25-30 interviews for a segmentation study. Include current customers, prospects, and churned customers. Churned customers are the highest-signal source.

## Step 4: Synthesize into a persona

After interviews or surveys, synthesize into a one-page persona using the structure in `references/persona-template.md`. Include:

- Name + role + company stage.
- Job to be done (the functional, emotional, and social job).
- Pain points, in their words.
- Consideration set (what alternatives they looked at).
- Buying process (who's involved, how budget moves).
- Must-haves, nice-to-haves.
- Channels they go to for information.

If you find distinct segments (by size, motivation, or buying behavior), build a persona for each. Two to four segments is typical; more than four usually means the hypothesis was too broad.

## Step 5: Test the persona on the launch plan

Before finalizing, pressure-test the persona against the GTM plan:

- Do the launch channels reach this persona? If they read trade pubs but we're running Instagram ads, rethink.
- Does the messaging speak their language? Use their words verbatim where possible.
- Does the sales process match how they buy?
- Is the persona big enough to hit the launch goals?

If the persona doesn't hold up, iterate. Better to catch this now than on launch day.

## Output format

When asked to define a target market, produce:

```
# Target Market: [Launch Name]

## Hypothesis (pre-research)
[Specific persona. Role, company, behavior, motivation, NOT-for.]

## Research plan
- Tactic: [interview / survey / conference / recruited panel]
- Sample size: [N]
- Incentive: [$X]
- Timeline: [start - end]
- Script: [link or attached]

## Findings
[What the research showed. Changes to the hypothesis.]

## Primary persona: [Name]
- Role, company, stage
- Job to be done
- Pain points (in their words)
- Consideration set
- Buying process
- Channels
- Must-haves / nice-to-haves

## Secondary personas (if any)
[...]

## NOT-for
[Explicit exclusions.]

## Implications for the launch
- Channels to use / drop
- Messaging notes
- Sales process notes
- Size check against launch goals
```

## What to avoid

- Never accept "everyone" as a target.
- Never use buyer personas someone else made for a different product without validating them.
- Never skip talking to churned customers; they're the richest source.
- Never outsource all the interviews. The PMM should run at least a handful personally to hear the language.
- Never build the persona before the research; the hypothesis is starting material, not the answer.

## References

- `references/jtbd-script.md` — the full Jobs to Be Done interview script (adapted from Christensen).
- `references/research-tactics.md` — detailed how-to for each of the six tactics.
- `references/persona-template.md` — the one-page persona template.
- `references/segmentation-guide.md` — how to find segments in the research and when to stop splitting.

## Examples

- `examples/persona-adroll-style.md` — a worked persona from a JTBD-style interview study.
- `examples/quick-survey-plan.md` — a two-week email survey plan with script and analysis.
