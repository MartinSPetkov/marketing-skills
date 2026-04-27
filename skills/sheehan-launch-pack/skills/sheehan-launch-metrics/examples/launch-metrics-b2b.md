# Example: launch metrics plan and day-30 report (Acme Insights)

Continuing the Acme Insights example from other skills. Tier 1 launch of a new paid product analytics tier.

## Metrics plan (set before launch)

### Stakeholder success statements

| Stakeholder | Success statement | Top metric | Target | Window |
|---|---|---|---|---|
| CEO | "Launch delivers $2.5M new ARR and establishes us in the product analytics category." | New ARR attributable to launch | $2.5M | 6 months |
| CMO | "Launch lands the category narrative and brings in qualified demand." | Tier-1 press mentions | 12 | Launch month |
| CRO | "Sales is ready on day 1 and closes against Mixpanel/Amplitude." | Sales certification rate | 90% certified | By T-2 weeks |
| CPO | "Feature is adopted at target rate without support blowup." | 30-day retention on new feature | >= 40% | 30 days |
| VP CS | "Existing base upgrades and doesn't churn." | Upgrade rate of existing base | 40% | 6 months |

### Full metric set (7)

| Metric | Target | Window | Source | Baseline |
|---|---|---|---|---|
| Paid signups (new accounts) | 500 | 90 days | CRM | 60/month before launch |
| New ARR | $2.5M | 6 months | CRM / Finance | $400K/month |
| Tier-1 press mentions | 12 | Launch month | PR agency tracker | 0 per month (no recent launches) |
| 30-day retention on feature | 40% | 30 days | Product analytics | 28% on old feature |
| Existing base upgrade rate | 40% | 6 months | Billing system | 5% organic upgrade rate |
| Sales certification rate | 90% | T-2 weeks | Sales enablement | N/A |
| Support tickets on new feature | < 3 per 100 users | 30 days | Helpdesk | 2 per 100 on existing features |

### Dashboard

- Amplitude dashboard, built by analytics team (Liz).
- Google Sheet for exec-friendly summary, updated weekly.
- Daily Slack snapshot in #launch-insights for the first 2 weeks.

### Reporting cadence

- Launch day: Slack snapshot.
- Day 7: Slack post + short written update.
- Day 30: Full report to exec team + all-hands.
- Day 60: Shorter update, trend focus.
- Day 90: Final scorecard + debrief.

### Risks

- Baseline press mentions = 0 makes the "12" target feel ambitious; PR agency confirms 12 is realistic given a strong announcement.
- Retention target assumes activation in week 1; product needs to add the activation event before launch.

## Day 30 report

### Headline

Behind on new ARR, ahead on adoption. Launch landed the category story and sales is ready; the pace of paid conversion is slower than planned because pricing is being negotiated on larger deals. Recommend holding course on product and messaging; adjust pipeline tactics for the next 60 days.

### Results

| Metric | 90-day target | Day 30 actual | On track? | Notes |
|---|---|---|---|---|
| Paid signups | 500 | 95 | N | Pace = 285 over 90d at current rate |
| New ARR (6mo) | $2.5M | $380K booked | N | $1.6M in pipeline, longer cycles than expected |
| Tier-1 press | 12 | 14 | Y | TechCrunch, The Verge, Protocol, InfoQ, 10 others |
| 30-day retention | 40% | 47% | Y | Beta users + early signups strong on core workflows |
| Existing base upgrade | 40% (6mo) | 8% | Y | On pace |
| Sales cert rate | 90% | 95% | Y | Hit before T-2 weeks |
| Support tickets | < 3/100 | 2.1/100 | Y | No product issues |

### What worked

- Press strategy beat the target by 16%. Analyst briefings in week 1 before embargo helped. Dev's blog post hit Hacker News and drove 12% of trial signups that week.
- Sales certification beat the target. Maria's team took it seriously; the new rubric was enforced.
- Product adoption held up; no quality or reliability issues.
- Upgrade motion is on pace for 6 months; CS outreach to top 50 accounts converted 6 accounts in 30 days.

### What didn't

- New-signups pace is behind. Top cause: larger deals (>$20K) are taking longer than assumed; sales cycle running 45 days versus planned 30.
- LinkedIn paid performed below forecast. CTR 0.6% versus 1.2% forecast. CPA $220 versus $140 target.
- Free trial to paid conversion is 14% versus 22% forecast. Reviews of the product flow show friction at the "invite teammates" step.

### What we're changing

- Shifting $40K of LinkedIn budget to retargeting + Google brand search, which outperformed forecast.
- Adding a 30-day discount for teams upgrading; CFO approved 10% off.
- PM and Design sprinting on the invite-teammates flow; release by day 45.
- Repricing larger deals to align with procurement cycles at mid-market (net-60 payment option added for $30K+ deals).

### Customer stories

- "I had a dashboard in 40 minutes and my CEO had it Monday morning. We'd have spent 3 months setting up Mixpanel." (VP Product, Latitude, name + logo approved for case study.)
- "The thing that sold us was the flat price. My CFO approved it in an email." (CFO, Nimbus, quoted anonymously.)

### Thanks

To Raj for shipping a clean beta, Dev for the HN-worthy post, Tom at Warm Room for crushing the press push, Maria for certifying the whole sales team in under 3 weeks, and Sam for the top-50 account outreach that pulled in 6 upgrades. And to every beta customer who stuck with us through an occasionally rough pre-launch product.

### Next checkpoint

Day 60: June 25. Day 90 final scorecard + debrief: July 24. Dashboard live at [link].
