---
name: sheehan-gtm-plan
description: Build a go-to-market (GTM) plan using Mary Sheehan's framework from The Pocket Guide to Product Launches. Use whenever a user says "build a GTM plan," "launch checklist," "go-to-market template," "should I launch this," "plan a product launch," "tier this launch," "bundle these features," "what goes in a launch plan," or asks how to organize a product or feature launch end-to-end. Also use when the user has many upcoming launches and needs help sizing them (Tier 1 / 2 / 3), grouping related features into a single launch story, or deciding which product stage (alpha, beta, GA) to announce publicly. Apply this skill BEFORE jumping into individual launch assets, because the GTM plan anchors everything else.
---

# Sheehan GTM Plan

Build a go-to-market plan the way Mary Sheehan builds one. The plan is the single source of truth for a launch: strategy, checklist, milestones, goals, and channels, all in one live document that gets updated weekly and shared with every stakeholder.

A GTM plan is not a checklist. It is the strategy for how the company will reach current and prospective customers with a differentiated value proposition, expressed through milestones, goals, and channels that everyone can see. Without one, marketing and sales scramble and customers end up confused.

## When to use this skill

Trigger on any of these requests:

- "Build me a GTM plan for [product/feature]."
- "What should go in a launch plan?"
- "Help me decide if this launch is Tier 1, 2, or 3."
- "I have 12 features shipping next quarter. How do I bundle them?"
- "Should we launch this in beta or wait for GA?"
- "We're about to launch, what's the checklist?"

If the user has already done the plan and is asking about a specific part (positioning, metrics, timing, team), route them to the matching Sheehan skill instead.

## Step 1: Decide whether to launch at all

Before any plan, answer: should you launch? Not every release warrants a marketing launch. A back-end speed improvement or invisible refactor is worth celebrating internally, not in market.

Ask the user to answer yes/no on five questions from the book. If two or more are yes, a launch is warranted:

1. Do you have product adoption, usage, or revenue goals tied to this release?
2. Have customers been asking for this product or feature?
3. Is this a game-changer for your industry?
4. Can a customer purchase what you are releasing (rather than a free feature update)?
5. Will the external release improve your competitive position?

If fewer than two are yes, recommend an internal-only announcement and stop.

## Step 2: Set the launch strategy (the "Key Info" tab)

Before the checklist, capture the strategy on one page. Sheehan calls this the Key Info tab of the GTM plan. It answers who, what, where, when, and why, plus what the launch is NOT about.

Fill in these fields with the user:

- **Who (target market).** The launch audience, defined as specifically as possible. Include who it is NOT for.
- **Who (internal team).** The internal launch team and RACI. Name the exec sponsor.
- **What (product stage).** Alpha, closed beta, open beta, or GA. See the product stage reference.
- **When (launch milestones).** Key stepping-stones backing into the launch date.
- **Where (top channels).** External channels (press, email, ads) and internal channels (all-hands, sales enablement, Slack).
- **Why (goals).** The top 2-3 business goals this launch rolls up to (revenue, MQLs, adoption, retention). Be specific, e.g. "500 active users in month one," not "drive adoption."

If the user cannot answer the "who is this NOT for" question, push them. The strategy is as much about what you are not doing as what you are.

## Step 3: Pick the tier

Tiers set expectations for resources, story size, and market reception. Everything-is-Tier-1 is a trap: the market and sales team become fatigued.

- **Tier 1.** The biggest launch of the quarter. Game-changing for customers or category. Full PR, event, sales certification, exec sponsorship, post-launch rolling thunder. One to two per quarter maximum.
- **Tier 2.** Important to sales and core customers but not category-changing. Blog, email, sales enablement, in-product messaging. No external PR push.
- **Tier 3.** Cosmetic updates, bug fixes, small UI changes. Changelog, help center, in-product note. No external promotion. Dozens per quarter is normal.

Tiers do not reflect engineering effort. A six-month back-end rewrite is often a Tier 3 because customers don't see it. Push back on teams who want to celebrate private wins with a public launch.

See `references/tiering-decision.md` for a decision tree.

## Step 4: Decide whether to bundle

If the user has several small features shipping in the same window, check if they can be bundled into a single launch story. Bundling makes smaller launches feel bigger and gives the market a coherent narrative.

Criteria for bundling:

- Features share a theme (e.g., "faster insights," "smoother integrations").
- Features serve the same core persona.
- Features can be tied to an upcoming event, conference, or calendar moment.

Sheehan's Firstup/SocialChorus example bundled 12 Tier 2 features as "Innovation Lab" and won Best Product Launch at Amplify 2018. The features were already shipped; the bundle created the story.

## Step 5: Fill in the four sections of the checklist

The GTM plan has four sections after the Key Info tab. Use Google Sheets or an equivalent shared doc so stakeholders can comment in real time.

**Section 1: Strategic Readiness.** Restate the who/what/when/where/why/how. Confirm target market, personas, competitive landscape, positioning, messaging, channel plan, and KPIs are all in progress or done.

**Section 2: External Promotion.** Channels the target audience will see the message through. See `references/external-channels.md` for the full channel menu with cost and tier guidance (press, paid digital, SEO, email, case studies, in-product messaging, blog, website update, help center, social).

**Section 3: Sales Enablement.** Internal channels for arming the sales team. See `references/sales-enablement.md` (all-hands, KPIs/incentives, one sheet, sales certification, pitch script, asset management, sales training, slides, internal FAQ/comm doc).

**Section 4: Internal Launch Communications.** How you keep colleagues informed and excited. Organize by timing leading up to launch. See the `sheehan-launch-team` skill for the full treatment of internal comms.

## Step 6: Plan the rolling thunder

Launch day is not the finish line. Plan post-launch momentum during launch planning, not after. Core content pieces to re-slice:

- Research white paper with shareable stats.
- Video featuring customers, employees, or the product.
- Customer events (advisory board, user conference).
- Customer case studies, then heavy promotion of those case studies.
- Infographic with the research paper's stats.
- Webinar series.
- Direct mail for high-value accounts (pair with email or ABM).
- Paid digital behind everything above.

Get stakeholder approval on rolling thunder before launch, not after.

## Output format

Default output: a Markdown GTM plan with these sections in order:

```
# [Product Name] GTM Plan

## Launch go/no-go
[Answers to the 5 yes/no questions. Recommendation.]

## Key Info
- Who (target market):
- Who (internal team + RACI):
- What (product stage):
- When (launch milestones):
- Where (top channels):
- Why (goals, with numbers):
- NOT for:

## Tier
[T1 / T2 / T3 with reasoning.]

## Bundle decision
[Standalone, or bundled with what / why.]

## Section 1: Strategic Readiness
[Checklist items with owner and due date.]

## Section 2: External Promotion
[Channel plan, picked from the reference menu.]

## Section 3: Sales Enablement
[Assets and dates.]

## Section 4: Internal Launch Communications
[Cadence and channels.]

## Rolling Thunder
[Post-launch momentum plan.]
```

If the user asks for a Google Sheet or Excel version, produce the same structure as an xlsx with one tab per section. If they don't specify format, default to Markdown and offer to convert.

## What to avoid

- Don't default everything to Tier 1. Push back.
- Don't accept "everyone" as a target market. See `sheehan-target-market`.
- Don't write goals as verbs without numbers. "Drive adoption" is not a goal. "500 active users by day 30" is.
- Don't let product or engineering set the launch date. Product marketing proposes the date, with input from PM. See `sheehan-launch-timing`.
- Don't skip the "who is this NOT for" line. It sharpens everything downstream.

## References

- `references/tiering-decision.md` — decision tree for Tier 1/2/3.
- `references/product-stages.md` — alpha/closed beta/open beta/GA definitions, goals, and launch activities per stage.
- `references/external-channels.md` — external promotion channel menu with cost and tier guidance.
- `references/sales-enablement.md` — sales enablement asset menu.
- `references/launch-checklist-sections.md` — full structure of the four checklist sections.

## Examples

- `examples/gtm-plan-b2b-saas.md` — a B2B SaaS Tier 1 launch plan.
- `examples/gtm-plan-feature-bundle.md` — a bundled Tier 2 launch of three related features.
