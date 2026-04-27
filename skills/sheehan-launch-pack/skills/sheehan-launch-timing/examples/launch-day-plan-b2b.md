# Example launch day plan (Acme Insights, Tier 1 B2B)

Continuing the Acme Insights example. Launch date: Thursday, June 26. Tier 1 analytics product.

## Launch date and time

- **Date:** Thursday, June 26
- **Time:** 8:00am PT / 11:00am ET
- **Rationale:** Mid-week after mid-quarter, no conflicting events, post-Memorial Day fully in the Q3 cycle.

## Core team on-call

| Role | Name | Coverage window |
|---|---|---|
| Launch lead (PMM) | Jane | 6am PT - 8pm PT |
| PM | Raj | 6am PT - 8pm PT |
| Eng lead | Sarah | 6am PT - 8pm PT |
| Growth / Lifecycle | Priya | 6am PT - 6pm PT |
| Content / Comms | Dev | 6am PT - 6pm PT |
| Support lead | Liam | 6am PT - 10pm PT (extended) |
| CS lead | Sam | 7am PT - 6pm PT |
| PR lead (external) | Tom at Warm Room | 6am PT - 4pm ET |

War room: #launch-insights-warroom (new channel)
Escalation: Jane (primary), VP Product (backup)

## T-1 day (Wednesday, June 25)

### Morning

- [x] Assets frozen at 9am.
- [x] Homepage final review in staging (Dev + Jane).
- [x] Blog post final review (Dev + legal + Jane).
- [x] In-product banner tested on staging (Raj).
- [x] Press release distribution confirmed for 11:00am ET via Business Wire (Tom).
- [x] All scheduled campaigns confirmed: external email (Priya), paid (Priya), social (Priya).

### Afternoon

- [x] 5-min all-hands preview at 2pm PT (Jane).
- [x] Swag (Acme Insights notebooks + stickers) delivered to office, remote team packages in mail.
- [x] Custom emoji :insights-launch: enabled in Slack.
- [x] War room channel set up.

### Evening

- [x] Everyone on core team verified logins.
- [x] Tom confirmed embargo with 14 reporters.

## Launch day (Thursday, June 26)

### 6:00am PT (T-2 hours)

- [ ] Jane in the war room.
- [ ] Core team online.
- [ ] Jane posts: "Good morning team, launch is go. Check-in at 7am."

### 7:00am PT (T-1 hour)

- [ ] Homepage pushed to production behind feature flag (Dev).
- [ ] Blog post final review, scheduled to publish at 8:00am PT.
- [ ] Press release confirmed for 11:00am ET (Tom).
- [ ] Sales day-1 FAQ email sent to full sales team (Jane).

### 8:00am PT (T-0, launch moment)

- [ ] Homepage hero swap (Dev).
- [ ] Blog post goes live (Dev).
- [ ] Press release distributes via Business Wire (Tom).
- [ ] In-product announcement enabled (Raj).
- [ ] External email sends via Marketo (Priya).
- [ ] LinkedIn + Google paid campaigns live (Priya).
- [ ] Launch moment Slack post in #general (Jane).
- [ ] First press pickup monitoring (Tom).

### 8:15am PT

- [ ] Verify all channels live.
- [ ] Mobile rendering check on homepage and blog.
- [ ] Signup flow end-to-end test with a test account.
- [ ] Payment flow test on upgrade page.

### 9:00am PT (T+1 hour)

- [ ] Paid CTR check. Pause anything visibly broken.
- [ ] Sales live question flood: Jane in #launch-insights-sales answering.
- [ ] Support ticket volume check (Liam).

### 12:00pm PT (T+4 hours)

- [ ] Mid-day snapshot: signups, visits, press. Post in #launch-insights.
- [ ] Social engagement check.
- [ ] CS first-touch check with top 10 accounts.

### 4:00pm PT (T+8 hours)

- [ ] End-of-day snapshot posted.
- [ ] Launch celebration: virtual happy hour at 5pm PT.
- [ ] Any incidents logged for the debrief doc.

## Day 2 (Friday, June 27)

- Morning: Day-1 metrics summary posted.
- Priya adjusts paid campaigns based on day-1 performance.
- Jane reviews sales questions from day-1, updates FAQ.
- Tom follows up with missed press pickups.

## Dress rehearsal (Saturday, June 21)

Core team on the call, 90 minutes, walked the entire launch day checklist in real time. Found:

- Homepage CTA was pointing to old signup URL (fixed).
- External email had a broken link in the "Learn more" button (fixed).
- In-product banner was firing for internal users (added exclusion rule).
- Press release embargo time was 10am ET, not 11am ET (corrected).
- Slack launch emoji wasn't loading in mobile (workaround: emoji added via Slack admin).

Worth the 90 minutes.

## Go/no-go decision (held June 19, T-1 week)

Criteria met:

- [x] Product GA-quality (no sev-1s).
- [x] 95% of reps certified.
- [x] All external assets final.
- [x] Press embargo set with 14 reporters.
- [x] Dashboards and tracking live in Amplitude.

Decision: GO. Signed by VP Product.
