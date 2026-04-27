# Sheehan launch pack

Six product-launch skills built from Mary Sheehan's *The Pocket Guide to Product Launches* (Lola Jane Press, 2023). Each skill maps to one part of the book and can be used on its own or chained with the others for a full launch cycle.

## What's in here

| Skill | Book part | When to use it |
|---|---|---|
| `sheehan-gtm-plan` | Part 1: Build the launch plan | First. The GTM plan anchors everything else. |
| `sheehan-target-market` | Part 2: Identify the target market | After the GTM plan, before messaging. Interviews, personas, segmentation. |
| `sheehan-launch-team` | Part 3: Align the launch team | After scope is set. RACI, PMM/PM split, 10% internal comms rule. |
| `sheehan-positioning-messaging` | Part 4: Create positioning and messaging | After target market is known. Positioning statement, messaging house, competitive matrix. |
| `sheehan-launch-metrics` | Part 5: Track metrics and measure success | During planning to set goals, and post-launch to report. |
| `sheehan-launch-timing` | Part 6: Pick dates and run launch day | Early to pick the date, late to run the day-of checklist. |

## How to use the skills together

A full Tier 1 launch touches all six. A typical sequence:

1. **Week -12.** Run `sheehan-gtm-plan` to tier the launch, bundle the features, and draft the plan.
2. **Week -11 to -8.** Run `sheehan-target-market` for JTBD interviews and personas. In parallel, `sheehan-launch-team` to set up RACI and internal comms.
3. **Week -10 to -8.** Run `sheehan-positioning-messaging` to build the messaging house.
4. **Week -8.** Run `sheehan-launch-metrics` to define goals and instrument tracking.
5. **Week -12 and week -1.** Run `sheehan-launch-timing` for date selection (week -12) and launch day runbook (week -1).

For Tier 2 launches, compress to 6 weeks and skip analyst briefings, sales certification, and dress rehearsal. For Tier 3, a two-week plan with a blog post and a changelog entry is usually enough.

## Skill structure

Each skill follows the same layout:

```
skills/<skill-name>/
  SKILL.md              # main skill file with YAML frontmatter
  references/           # detailed reference files loaded on demand
  examples/             # 1-2 worked examples in different contexts
  evals/
    evals.json          # 3 test cases with assertions
```

The `SKILL.md` file gives the framework and tells the model which reference files to pull in. References are loaded only when relevant, to save context.

## Example narrative

Two recurring examples run through most of the skills:

- **Acme Insights**, a B2B SaaS analytics company running a Tier 1 launch. Shows up in GTM plan, launch team, positioning, metrics, and timing examples.
- **SnapFit**, a consumer fitness app. Shows up in metrics and positioning examples to contrast with B2B.

## Writing style

All skills were written to avoid AI-writing patterns. No em dashes, no banned marketing words, sentence-case headings, concrete examples with named characters. If a generated output from any skill doesn't read this way, something's off and the skill needs a tune-up.

## Credits

Frameworks in this pack come from Mary Sheehan's book. The skill structure, examples, and evals are original. If you want the full book, get it at [Lola Jane Press](https://lolajanepress.com/).

## Known issues

An empty `skills/sheehan-messaging-house/` folder exists as a leftover from the initial scaffolding. The real Part 4 skill lives in `skills/sheehan-positioning-messaging/`. The empty folder is benign but can be removed with admin permissions.
