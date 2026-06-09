# Outbound engine config (demo)

## Sender identity
Name: the founder
Company: Catalyst (gotcatalyst.com)
Offer: helps B2B companies get cited in AI search and turn content into pipeline.
Voice: direct, specific, no filler. See antislop_rules.md.

## Booking
Booking link: https://cal.com/catalyst/intro
Default meeting: 30 minutes, intro call.

## ICP
Target roles: VP, Head, or Director of Marketing, Growth, Demand Gen, or Content; RevOps lead; founder or CEO at companies under ~150 who still own marketing.
Company size: 50 to 500, B2B SaaS.
Disqualifiers: students, solo consultants, pure IC sales (SDR, AE) with no marketing remit, companies under ~10 or over ~1,000, anyone outside B2B SaaS.

## Sequence (day offsets from connection accepted)
- Day 0: connection note (under 300 characters)
- Day 1: message 1
- Day 4: message 2 (only if no reply)
- Day 8: email follow-up (optional channel)
A positive reply stops the sequence and books a meeting. A negative reply stops it.

## Daily caps (enforced even in dry-run)
- Connection requests per day: 25
- Messages per day: 40

## Scoring weights
Fit weight: 0.5
Intent weight: 0.5
Intent components:
- engagement type: comment 1.0, repost 0.6, like 0.3
- recency: within 7 days 1.0, within 14 days 0.6, older 0.2
- repeat engagement: +0.2 per additional post engaged, capped at +0.4
- post intent: high-intent topic (e.g. AI search visibility) 1.0, medium 0.6, low 0.3
Tiers: Hot >= 80, Warm 60 to 79, Cool below 60.
