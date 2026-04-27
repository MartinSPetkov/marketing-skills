# Measurement pitfalls

Common ways launch measurement fails. Avoid each one.

## 1. No baseline

**Symptom:** "We got 1,000 signups in the first month!"
**Problem:** Without the pre-launch baseline, the number is meaningless. If you averaged 900 signups a month before launch, you moved the needle by 11%.
**Fix:** Pull 3-6 months of pre-launch data for every metric you'll report. Include it in the first column of the scorecard.

## 2. Tracking gaps at launch

**Symptom:** "Turns out we didn't tag the launch page in GA until week 2."
**Problem:** Now you've lost your most important data window.
**Fix:** QA tracking 2 weeks before launch. Walk the flows. Check events fire in the right tool. Check campaign tags on every external link.

## 3. Attribution disputes

**Symptom:** Marketing and sales disagree about whether a signup came from the launch or from regular demand.
**Problem:** You'll spend more time arguing about credit than doing the work.
**Fix:** Agree on attribution before launch. Use UTMs consistently, tie to a single source-of-truth system (usually a CRM or product analytics tool), document the rules, and resolve edge cases in writing.

## 4. Too many metrics

**Symptom:** A 15-metric scorecard that no one reads.
**Problem:** Noise hides signal. People tune out.
**Fix:** 5-7 metrics, max. Put the rest in an appendix.

## 5. No target

**Symptom:** "We want to see strong adoption."
**Problem:** Every number is defensible as "strong" after the fact.
**Fix:** Every metric has a number attached. "60% activation in 30 days" beats "strong activation."

## 6. Target without source

**Symptom:** "$2.5M new ARR in 6 months." Great, but what system reports that, filtered to this launch, on what cadence?
**Fix:** For every metric, name the report, the query, and the refresh frequency.

## 7. Reporting vanity numbers

**Symptom:** "50 million impressions." "Reached X audience." "Went viral."
**Problem:** Reach is cheap and often meaningless. Nobody's career depends on impressions.
**Fix:** Cut vanity metrics from the scorecard unless they tie directly to a downstream action.

## 8. Spin

**Symptom:** The day-30 report frames a miss as "early momentum."
**Problem:** Execs see through spin. Trust erodes. The next launch report gets less attention.
**Fix:** Lead with the real read, good or bad. Save the team's credibility for the launches that genuinely worked.

## 9. Moving the target

**Symptom:** 60 days in, the target quietly changes from "$2.5M new ARR" to "$1M pipeline."
**Problem:** Nothing can be measured against a moving target.
**Fix:** If the target needs to change, write up why, share with stakeholders, mark the original target and the revision clearly in the report.

## 10. Launch ends, measurement ends

**Symptom:** Day 30 report goes out, then silence.
**Problem:** Many launch metrics mature at 90-180 days (renewal, expansion, retention).
**Fix:** Put day 60, day 90, day 180 checkpoints on the calendar at launch time.

## 11. Not comparing to other launches

**Symptom:** Every launch is evaluated in isolation.
**Problem:** Teams can't tell if a launch did well relative to past launches.
**Fix:** Keep a launch log. Day 30, 60, 90 numbers for every launch. Over time, you'll see what's typical and what's exceptional.

## 12. Only measuring external

**Symptom:** All metrics are revenue, adoption, and press. Internal readiness isn't measured.
**Problem:** Internal readiness (sales cert, CS readiness, internal comms) predicts external outcomes. If you don't measure them, you can't improve them.
**Fix:** Include internal metrics: sales certification rate, CS preparedness survey, internal awareness survey at launch week.

## 13. Customer measurement delay

**Symptom:** Customer NPS and satisfaction data takes 90 days to come back.
**Problem:** You can't adjust in-flight.
**Fix:** Quick-turn customer signal: post-launch in-product surveys (1 question, fires on first use), support ticket sentiment, CS account-level check-ins at week 2.

## 14. Ignoring negative signal

**Symptom:** A metric is moving in the wrong direction; team doesn't surface it.
**Problem:** Small problems compound. Churn or support spikes caught early are fixable.
**Fix:** Treat any metric moving opposite of expected as a priority in the next launch sync, even if other metrics are green.

## 15. Never debriefing

**Symptom:** Day 30 report published. Six months later, the next launch has the same issues.
**Problem:** No mechanism to carry forward learnings.
**Fix:** The day-90 debrief (see `sheehan-launch-team`) feeds back into the next launch plan. Keep a running "what we learned" doc.
