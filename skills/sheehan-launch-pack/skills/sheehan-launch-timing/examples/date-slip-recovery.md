# Example: date slip recovery (Acme Insights)

What happened when Acme Insights had to move a Tier 1 launch date from June 26 to July 17. Written up so the team learns from it and the pattern doesn't repeat.

## The original plan

- Launch date: Thursday, June 26.
- Tier 1 product launch (new analytics workspace).
- 12-week plan, kicked off mid-April.
- Press embargo set with 14 reporters for June 26 at 8am PT.
- Sales certification target: 90% by June 12 (T-2 weeks).

## What went wrong

At T-3 weeks (June 5), two things hit in the same week.

**First**, an exec review surfaced a positioning concern. The VP of Marketing felt the "workspace" framing wasn't landing in customer interviews Dev had run in late May. Three out of five interviewees said "workspace" sounded generic and reminded them of Notion or Slack. The messaging house was built on "workspace" as the category term.

**Second**, a sev-1 bug was found in the new shared-dashboard feature. Engineering estimated 2 weeks to fix and test, which would leave no buffer before June 26.

Either one of these alone might have been survivable. Both together, at T-3 weeks, meant the launch was not going to land well.

## The decision (June 8, T-2.5 weeks)

Jane (PMM launch lead) called a go/no-go discussion three weeks earlier than scheduled. Present: VP Product (exec sponsor), VP Marketing, Raj (PM), Sarah (Eng lead), Tom (PR agency).

Framing: we can ship on June 26 with the bug fixed but the positioning unresolved, or we can move the date.

Risks of shipping on June 26:
- "Workspace" framing lands flat. Low press pickup.
- Sales reps who were certified on the "workspace" pitch start improvising. Inconsistent positioning in the field.
- Customer confusion about what the product actually is.

Risks of moving the date:
- Press embargo has been set. Some reporters already shifted coverage plans.
- Team fatigue. Eng and PMM have been at it since April.
- Competitor (Mixpanel) rumored to have something launching in July.

Decision: move to July 17. Three weeks. Enough time to redo the positioning work (2 weeks), re-certify reps on the new messaging (1 week), and absorb the eng slip (2 weeks in parallel).

VP Product signed the decision in writing. Jane sent the internal note.

## The recovery plan

### Week of June 8 (T-5 weeks from new date)

- Jane ran a positioning reset workshop on June 10. New frame: "customer analytics, not product analytics." Differentiator from Mixpanel and Amplitude. Tested with 5 customer calls between June 11 and June 14.
- Tom (PR) called each of the 14 reporters individually. Script: "We're moving three weeks to sharpen the positioning. New date is July 17, same 8am PT. Embargo holds. Here's the new angle." 12 of 14 held the embargo. 2 dropped out (one had a conflict, one didn't want a re-pitch).
- Sarah scoped the bug fix. Confirmed 2 weeks to fix and test.

### Week of June 15 (T-4 weeks)

- New messaging house finalized June 17.
- New homepage copy drafted June 18, through legal review by June 20.
- Blog post rewritten June 19.
- Press release rewritten June 20.
- Sales re-certification scheduled for June 22-26.

### Week of June 22 (T-3 weeks)

- Bug fix complete June 24. In QA.
- Sales re-certification: 44 reps re-pitched with new messaging by June 26. 92% passed.
- Analyst re-briefings scheduled for June 29-July 3 (Gartner, Forrester).

### Week of June 29 (T-2 weeks)

- Bug fix in production on June 30.
- Analyst re-briefings happened. Two of three analysts preferred the new framing.
- External assets final review.

### Week of July 6 (T-1 week)

- All-hands preview (5 min).
- Go/no-go meeting July 10. GO.
- Dress rehearsal July 12.

### July 17: launch

Executed on plan. 11 of 12 held reporters published. Press pickup was noticeably stronger than the June 26 positioning would have produced: three "customer analytics" stories framed the whole news cycle on the new angle.

## What the slip cost

- Real dollar cost: roughly $15k in PR agency re-work and extra sales training time.
- Opportunity cost: three weeks of exec attention.
- Team cost: two weekends of crunch work on positioning and re-certification.

Worth every dollar. A June 26 launch with "workspace" positioning would have been a quiet launch.

## What we would do differently

Three things went into the post-mortem.

**Customer interviews should have happened at T-8 weeks, not T-4.** If the "workspace" framing had been tested in April, the positioning reset would have been 6 weeks earlier and no date slip.

**Bug discovery at T-3 weeks was too late.** The eng team had been testing happy-path flows. Edge cases weren't exercised until QA at T-4 weeks. We're adding an "integration week" at T-6 weeks going forward, where eng runs the full feature through end-to-end scenarios before the launch plan goes into T-5 rehearsal mode.

**The go/no-go criteria at T-8 weeks didn't include "positioning validated with customers."** It included "messaging signed off by exec." Exec sign-off is not the same as customer validation. New criterion added.

## How we communicated the slip

Internal first. Slack post from VP Product on June 9: "We're moving the launch three weeks, from June 26 to July 17. Two reasons: positioning needs sharpening based on customer feedback, and a sev-1 bug needs two weeks to fix. Better to ship something we're proud of. Full note in the #launch-insights channel. Thanks for the hard work."

External (press) second. Tom called reporters over two days. No email blast; each reporter got a personal call or email.

Customer-facing: none at that stage. No public date had been promised. The launch was internal until July 17.

## The rule

If you have to slip, slip once, slip cleanly, and write up why. Sheehan's line: "The worst slip is a 10-day slip, then another 10-day slip, then another. Make the call, move the date decisively, and hit the new one."

We hit July 17. Lesson filed.
