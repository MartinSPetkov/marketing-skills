# Example: launch metrics plan for a consumer mobile app (SnapFit)

Continuing the SnapFit example from the positioning-messaging skill. Consumer fitness app, major iOS and Android launch.

## Stakeholder success statements

| Stakeholder | Success statement | Top metric | Target | Window |
|---|---|---|---|---|
| CEO | "Launch establishes SnapFit as the time-constrained fitness choice and builds a base of paying users." | Paid subscribers | 40,000 | 90 days |
| Head of Growth | "CAC is under target and retention holds through month 2." | CAC payback | < 60 days | Ongoing |
| Head of Product | "Users who try the app come back." | Day-30 retention | >= 35% | 30 days |
| Head of CX | "Users succeed at their workouts and rate the app well." | App store rating | >= 4.6 stars | 30 days |

## Full metric set (6)

| Metric | Target | Window | Source | Baseline |
|---|---|---|---|---|
| Installs | 400,000 | 90 days | App Store Connect / Play Console | 3,000/month pre-launch waitlist |
| Paid subscribers | 40,000 | 90 days | Revenuecat | N/A |
| Activation (1st workout completed) | 60% | Day 7 per cohort | Amplitude | Tested at 55% in beta |
| Day-30 retention | 35% | Day 30 per cohort | Amplitude | Tested at 28% in beta |
| App store rating | 4.6 stars | Day 30 | App Store / Play | N/A |
| CAC payback | 60 days | Ongoing | Revenuecat + ad platforms | N/A |

## Dashboard

- Amplitude chart suite for funnel and retention.
- Revenuecat dashboard for subscription.
- Weekly Google Sheet digest for exec team.

## Reporting cadence

- Launch day: Slack snapshot every 4 hours for the first 24 hours.
- Day 3: First install and activation read.
- Day 7: Subscription conversion read.
- Day 30: Full report + all-hands share.
- Day 60: Retention trend read.
- Day 90: Final scorecard.

## Risks

- Day-30 retention is a lagging metric; early signal is day-3 and day-7 retention.
- App Store rating is a censored metric; bad first reviews can drag averages for months. Mitigation: in-app rating prompt fires only after 3 completed workouts.
- Paid acquisition CACs spike during launch window; CAC payback metric will look worse than steady state.

## Learnings from pre-launch test (2-week soft launch in Canada and Australia)

- Activation was 55%, below 60% target. The onboarding had 6 screens; testing shows 3-screen onboarding converts at 62%. Shipping change at GA.
- Day-7 retention was 52%, predicting day-30 at ~35%. On track.
- Subscription conversion at day 7 was 9%, target is 10%. Price test showed $9.99/mo converts at 11% versus $12.99 at 8%. Going with $9.99 at GA.

## What's different for consumer versus B2B

- Volume-heavy metrics (hundreds of thousands of installs versus hundreds of signups).
- Retention is the most important metric, not revenue at launch.
- App store reviews are a core marketing signal, not just a satisfaction signal.
- No sales enablement, so the "internal readiness" metric is customer support training and FAQ preparation.
- Press is still relevant but ranks below paid acquisition in driving volume.
