---
name: sheehan-launch-metrics
description: Plan, measure, and report launch metrics using Mary Sheehan's "3 Steps to Metrics Success" framework from The Pocket Guide to Product Launches. Use whenever a user says "how do we measure this launch," "what are the right KPIs for a launch," "build a launch dashboard," "report on launch results," "how did our launch do," "post-launch analysis," "day-30 metrics," "launch scorecard," "what should we track," "tell me if the launch worked," or any request about choosing, instrumenting, or reporting launch metrics. Apply this skill DURING GTM planning (to set goals) and AFTER launch (to report). Do NOT use this skill for general product analytics or company-wide KPI trees; this skill is scoped to one launch at a time.
---

# Sheehan Launch Metrics

If you can't say in a sentence what success looks like, the launch will be judged on vibes. Set specific numeric goals before launch, instrument to measure them, and write the results up even when they're bad.

## When to use this skill

Trigger on:

- "What metrics should we track for this launch?"
- "Build a launch dashboard."
- "Did the launch work?"
- "Write up the day-30 results."
- "Our CEO wants to see launch numbers."
- "How do I know if the messaging landed?"

Use at two points:

1. **During GTM planning.** Goals go in the Key Info section of the GTM plan (see `sheehan-gtm-plan`).
2. **Post-launch.** Day 7, day 30, day 60, day 90 reports.

## The 3 Steps to Metrics Success

Sheehan's framework, adapted for launches.

### Step 1: Define what success means

Before picking metrics, write a one-sentence success statement per stakeholder. Each stakeholder has a different definition.

- **CEO:** "This launch moves the top-line revenue number or pipeline number."
- **CMO:** "This launch lands the category story and brings in qualified leads."
- **CRO:** "Sales hits the new-ARR number attached to this launch."
- **CPO:** "The feature is adopted by X% of target users in Y days."
- **VP CS:** "Existing customers upgrade or renew at a higher rate."

Write these down. Share them with the stakeholder and get agreement. When launch day comes, whatever you measure will be judged against these statements, explicit or not.

### Step 2: Pick 5-7 metrics that map to the success statements

Not 20 metrics. Not 3. Somewhere between 5 and 7.

Categories:

- **Adoption.** Users activating the new product or feature.
- **Revenue.** Paid signups, new ARR, upgrade rate.
- **Awareness.** Press mentions, share of voice, direct traffic to launch pages.
- **Engagement.** Repeat usage, depth of use, feature retention.
- **Sales.** Pipeline generated, deal cycle time, win rate.
- **CS.** Support ticket volume, customer satisfaction, renewal rate.

Each metric has:

- **Numeric target.** "500 paid accounts in 90 days," not "lots of signups."
- **Measurement window.** Day 7, day 30, day 60, day 90.
- **Source.** Which system, which report, which query.
- **Baseline.** What's the comparable number from before the launch?

See `references/metric-menu.md` for the full menu by launch type.

### Step 3: Instrument and report

**Before launch:**

- Confirm every metric has a data source that'll be populated on launch day.
- Build a dashboard. A simple Google Sheet works fine for Tier 2 and below.
- Agree with the stakeholder on the reporting cadence.

**Launch day + 7 days:**

- Daily snapshot in the Slack channel.
- Short written update on day 7: what's ahead of plan, behind, on track.

**Day 30:**

- Full write-up. See `references/day-30-template.md`.
- Share with exec team and launch team.
- Present at company all-hands (5-10 minutes).

**Day 60 and 90:**

- Shorter updates. Focus on trends and adjustments.
- Day 90: final launch scorecard. What hit, what missed, what we learned.

## Step 1: During GTM planning, write goals per stakeholder

Ask the launch lead to fill in this table before finalizing the GTM plan:

| Stakeholder | Success statement | Top metric | Target | Window |
|---|---|---|---|---|
| CEO | [One sentence] | [Metric] | [Number] | [Days] |
| CMO | [One sentence] | [Metric] | [Number] | [Days] |
| CRO | [One sentence] | [Metric] | [Number] | [Days] |
| CPO | [One sentence] | [Metric] | [Number] | [Days] |
| VP CS | [One sentence] | [Metric] | [Number] | [Days] |

Get written agreement (even a Slack thumbs-up counts) from each stakeholder. This is the contract the launch will be judged against.

## Step 2: Pick the metric set

For most launches, use this scaffold and tune:

**Adoption and engagement:**

- X% of target users activate the new product in 30 days.
- X% of activators use it weekly at day 60.

**Revenue:**

- X paid signups in 90 days.
- $X new ARR in 6 months.
- X% of existing base upgrades to the new plan in 6 months.

**Awareness:**

- X press mentions in target pubs in launch month.
- X branded search lift.
- X direct traffic to launch page.

**Sales:**

- $X pipeline generated in 90 days from the launch campaign.
- Sales certification rate (Tier 1).

**CS:**

- Net negative churn (or stable) in the 6 months after launch.
- Support ticket volume per customer (should not spike).

Pick 5-7 total across categories. Any more becomes noise; any fewer leaves gaps.

## Step 3: Build the dashboard

Tools:

- Tier 1: Amplitude, Mixpanel, or Looker dashboard owned by analytics team. Supplement with a Google Sheet for exec-friendly view.
- Tier 2: Google Sheet. Update weekly.
- Tier 3: a single Slack post at day 7 and day 30.

Dashboard layout:

- Top: launch name, date, tier.
- Metric cards with target, current, and delta.
- One chart per metric showing trend vs. baseline.
- A short "headline of the week" section from the PMM.

## Step 4: Run the post-launch reviews

### Day 7: the early read

One paragraph in Slack.

- What shipped and when.
- Adoption snapshot (green/yellow/red).
- Top surprise: something that worked better than expected, or not.
- What we're watching.

### Day 30: the full read

1-2 page write-up. Use the template in `references/day-30-template.md`. Covers:

- Summary: did the launch hit its top goals?
- Results table (target vs. actual per metric).
- What worked.
- What didn't.
- What we're changing.
- Next milestone (day 60).

### Day 60: the mid-point

Focus on trends and adjustments. What's still moving? What stalled?

### Day 90: the final scorecard

Close the loop. Compare to launch plan goals. Write the debrief (see `sheehan-launch-team` for the team debrief process). Share with exec team.

## Step 5: Tell the truth in writing

Launches fail. Numbers miss. Write it up anyway. Sheehan's point: the team that writes honest post-launch reports gets better at launches. The team that only writes when things go well doesn't learn.

Tips for honest reporting:

- Lead with the headline, good or bad.
- Separate causes from excuses. "We missed by 30% because the ICP was wrong" is a learning. "We missed because Q4 was hard" is not.
- Call out what you'd change. If you wouldn't change anything, you haven't learned.
- Thank the team. By name. Publicly.

## Output format

When asked to build a launch metrics plan, produce:

```
# Launch metrics: [Launch name]

## Success statements per stakeholder
| Stakeholder | Statement | Top metric | Target | Window |
|---|---|---|---|---|
| CEO | ... | ... | ... | ... |
| CMO | ... | ... | ... | ... |
| ...

## Full metric set (5-7)
[Metrics with target, window, source, baseline]

## Dashboard
[Tool and URL or layout description]

## Reporting cadence
- Launch day: [snapshot]
- Day 7: [format]
- Day 30: [format, owner, audience]
- Day 60: [...]
- Day 90: [...]

## Risks and mitigations
[What could go wrong in the measurement; e.g., tracking gap, baseline unknown]
```

When asked to write a post-launch report, use the template in `references/day-30-template.md`.

## What to avoid

- Never launch without numeric goals agreed to in writing.
- Never pick metrics after launch. The "what did we want again?" question is a sign of failure.
- Never track 20 metrics. The team ignores most and the signal gets lost.
- Never skip the day 30 write-up. If you skip it, the team learns nothing.
- Never blame the market for missed goals before checking your own assumptions (ICP, pricing, channels).
- Never celebrate raw numbers without comparing to the baseline. 1,000 signups means nothing if you were already getting 900.

## References

- `references/metric-menu.md` - full menu of launch metrics by category and tier.
- `references/day-30-template.md` - standard post-launch write-up.
- `references/stakeholder-metrics-map.md` - what each stakeholder cares about and why.
- `references/measurement-pitfalls.md` - common measurement mistakes and how to avoid them.

## Examples

- `examples/launch-metrics-b2b.md` - metrics plan and day-30 report for a B2B SaaS launch.
- `examples/launch-metrics-consumer.md` - metrics plan for a consumer mobile app launch.
