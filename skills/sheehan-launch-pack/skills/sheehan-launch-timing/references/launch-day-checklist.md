# Launch day checklist (runbook)

Written two weeks before launch, read the day before, executed on the day. Every item has an owner and a timestamp.

## T-1 day (the day before)

### Morning (9am)

- [ ] Freeze all external assets. No edits unless blocking.
- [ ] Final review of homepage in staging. Check all links, CTA, hero.
- [ ] Final review of blog post in staging.
- [ ] Final review of in-product announcement in staging.
- [ ] Confirm all scheduled campaigns: email, paid, social.
- [ ] Confirm press release distribution time.

### Afternoon (2pm)

- [ ] 5-minute all-hands launch preview.
- [ ] Swag delivered to office (or confirmed shipped to home addresses for remote teams).
- [ ] Launch Slack emoji enabled.
- [ ] War room set up: dedicated channel, pinned doc of known issues, rotation confirmed.

### Evening (by 6pm)

- [ ] Everyone on the core team has tested their launch day logins and tools.
- [ ] Launch lead checks in on press embargo, confirms reporters ready to publish at T-0.
- [ ] Launch lead posts "see you at 7am" message in the core channel.

## Launch day

### T-2 hours (e.g., 6am if launch is 8am PT)

- [ ] Launch lead in the war room.
- [ ] Core team online.
- [ ] Final check of homepage, blog, in-product announcement in staging.

### T-1 hour (7am)

- [ ] Push homepage to production (but don't swap hero yet).
- [ ] Blog post scheduled to publish at T-0.
- [ ] Press release distribution confirmed for T-0.
- [ ] Sales team gets day-1 FAQ refresh in their inbox.

### T-0 (8am): launch moment

- [ ] Homepage hero swap.
- [ ] Blog post goes live.
- [ ] Press release distributes.
- [ ] In-product announcement enables.
- [ ] External email sends.
- [ ] Social posts publish.
- [ ] Paid campaigns turn on.
- [ ] Launch moment Slack post to the company.

### T+15 minutes

- [ ] Verify every channel is live.
- [ ] Check homepage load time and mobile rendering.
- [ ] Confirm signup flow works end to end.
- [ ] Check payment processing on upgrade page.
- [ ] First press pickup tracking.

### T+1 hour

- [ ] Paid campaign performance check. Pause any campaign with broken creative.
- [ ] Sales channel flood check: are reps getting live questions? Launch lead answers in the day-1 Slack channel.
- [ ] Support ticket volume check. Spike = triage.

### T+4 hours

- [ ] Mid-day snapshot in #launch-[name]: signups, visits, press mentions, known issues.
- [ ] Social engagement check: are people sharing? Any misinformation to correct?
- [ ] First customer response check in CS channel.

### T+8 hours

- [ ] End-of-day snapshot posted.
- [ ] Celebration moment: launch video or thanks message in Slack. Optional team dinner or virtual happy hour.
- [ ] Any incidents logged for debrief.

## T+1 day

### Morning

- [ ] Day-1 metrics summary posted.
- [ ] All follow-up press outreach on-schedule.
- [ ] Any paid campaign adjustments from day-1 performance.
- [ ] Customer email #2 (warm follow-up) scheduled for day 2 or 3.

### Afternoon

- [ ] Sales review: what questions came up? Update the FAQ.
- [ ] CS review: what issues? Any escalations?

## Known-issues doc structure

Shared Google Doc pinned in the war room channel. One section per category:

- **Product issues:** bugs, outages, broken flows.
- **Site issues:** 404s, rendering, performance.
- **Campaign issues:** broken links, misfired sends, paid campaign errors.
- **Messaging gaps:** questions the FAQ doesn't cover.
- **Press and analyst:** pickups, quotes, misattributions.

Each entry: timestamp, reporter, description, owner, status.

## Dress rehearsal (T-5 days)

Walk the launch day checklist in real time, in sequence. Core team on the call. Don't actually publish, but:

- Push to staging.
- Verify every link works in staging.
- Practice the launch moment Slack post, the first-hour check-in, the mid-day snapshot.
- Find broken things cheaply.

Rehearsal usually reveals 3-5 things that would have failed on the day. Worth every minute.

## Go/no-go criteria (agreed at T-8 weeks, reviewed at T-1 week)

A launch is go if:

- Product is GA-quality (no sev-1s, quality criteria hit).
- 90%+ of reps certified.
- All external assets final and reviewed.
- Press embargo list is set.
- Dashboards and tracking are live.

A launch is no-go if any of these are missing and can't be recovered in 48 hours.

Go/no-go decision at T-1 week. Documented. Signed by the exec sponsor.
