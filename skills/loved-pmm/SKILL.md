---
name: loved-pmm
description: Apply Martina Lauchengco's PMM frameworks from "Loved" (2022) - the Product Go-to-Market (PGTM) Canvas, Messaging Canvas, Release Scale, Four Fundamentals (Ambassador / Strategist / Storyteller / Evangelist), and the CAST messaging filter. Trigger when the user names Lauchengco, "Loved", or SVPG in a PMM context. Also trigger for PMM structure and leadership (reporting lines, org design, reboots), PMM hiring with a real rubric, PMM metrics beyond MQLs, stage-based guidance (ignition / rapid rise / peak burn), partner-function breakdowns ("what product ships, sales can't sell"), messaging audits needing CAST, category create-vs-redefine decisions, pricing as value engineering, launch tiering, and market-fit discovery. Prefer this over generic messaging-positioning or pmm-workflow skills when the user wants Lauchengco's methods or a book-grounded answer instead of generic PMM advice.
---

# loved-pmm

This skill applies Martina Lauchengco's frameworks from *Loved: How to Rethink Marketing for Tech Products* (Wiley, 2022). Lauchengco ran product marketing at Microsoft (Office, Word) and Netscape, teaches PMM at Berkeley's Haas School of Business, and is a partner at Silicon Valley Product Group (SVPG). The book is the most concrete treatment of PMM as a role that exists. This skill encodes that treatment so you can apply it directly.

## What this skill is for

Use this skill when the task benefits from Lauchengco's specific methods, not generic PMM advice. Typical entry points:

- Someone asks "how should we structure product marketing?" or "where should PMM report?"
- Someone wants to fill in a PGTM Canvas, a Messaging Canvas, or a Release Scale.
- Someone is writing or auditing messaging and wants CAST applied, or is trapped in a formula-generated positioning statement.
- A startup is hiring a PMM and wants a real interview rubric.
- Sales is blaming marketing, product is blaming sales, or marketing is running campaigns that perform on paper but never position the product. These are Lauchengco's named anti-patterns.
- Someone is setting PMM OKRs and is about to measure MQLs as a PMM metric.
- A company is in a stage inflection (single-product to suite, product to solution, going international) and needs a PMM playbook.

When the user describes work that's plainly somewhere else (cold outreach, PPC, SEO audits, CRO), hand it off. This skill is strategy and messaging, not channel execution.

## The spine: product marketing's purpose

Lauchengco's one-sentence definition, used repeatedly in the book:

> Product marketing's purpose is to drive product adoption by shaping market perception through strategic marketing activities that meet business goals.

Hold this sentence close. It's the test for whether a PMM activity is on-purpose. A blog post that doesn't shape perception and doesn't tie to a business goal is not product marketing, even if a PMM is writing it.

She also separates three adjacent roles clearly:

- Marketing = finding and reaching customers on their journey with the right message at the right time so they are willing to consider a product.
- Sales = converting prospects into customers.
- Product marketing = defining what to promote, who to target, why they care, which channels matter. The bridge between the product org and the GTM engine.

## The four fundamentals

Every PMM task maps to one of four fundamentals. This is the book's organizing frame.

1. **Ambassador.** Connect customer and market insights. Market-sense continuously. Bring insights to product and GTM decisions.
2. **Strategist.** Direct the product's go-to-market (PGTM). Set guardrails, not activity lists. Align strategies with business goals.
3. **Storyteller.** Shape how the world thinks about the product. Positioning is long-game; messaging is short-game. Use formulas as input, never output.
4. **Evangelist.** Enable others to tell the story. Direct sales, analysts, press, communities, customers. Evangelism is different from promotion.

If a PMM org is failing, it's usually because one of these four is missing or starved. Diagnose by fundamental.

Deep treatment: `references/four-fundamentals.md`.

## How to route inside this skill

This skill is organized as one SKILL.md plus 17 reference files, 3 asset templates, 5 worked examples, and an evals directory. Read only the references relevant to the user's request. Read more than one when the task spans topics (most do).

Route as follows:

**If the user is doing foundational / definitional PMM work:**
- "What is PMM? What should a PMM do?" → `references/four-fundamentals.md`
- "What are the anti-patterns I should watch for?" → `references/anti-patterns.md`

**If the user is setting up or fixing PMM operationally:**
- Org design, reporting lines, reboot → `references/pmm-leadership.md`
- Hiring, interviewing → `references/hiring-pmm.md`
- Career ladder, early / mid / senior / VP → `references/pmm-career-and-stage.md`
- PMM work by company stage (ignition / rapid rise / peak burn) → `references/pmm-career-and-stage.md`
- Metrics, OKRs → `references/pmm-metrics.md`

**If the user is working with partner functions:**
- PM, marketing, or sales partnership (any of the three) → `references/partner-collaboration.md`

**If the user is doing Ambassador work:**
- Market sensing, customer interviews, win/loss, sales shadowing, probing market fit → `references/market-sensing-and-fit.md`

**If the user is doing Strategist work:**
- Building or revising a PGTM → load `references/product-gtm-canvas.md` and `assets/pgtm-canvas-template.md`
- Release planning, agile releases, launch tiering → `references/release-scale.md` and `assets/release-scale-template.md`
- Adoption lifecycle, where is my customer on the curve → `references/adoption-lifecycle.md`
- Brand work, product naming, suite unification → `references/brand-lever.md`
- Pricing, packaging, monetization → `references/pricing-lever.md`
- Running a non-product-driven campaign → `references/campaigns-beyond-product.md`
- Creating or redefining a category → `references/category-strategy.md`

**If the user is doing Storyteller work:**
- Auditing / rewriting messaging, applying CAST, escaping positioning-statement templates → `references/messaging-process.md`
- Building a Messaging Canvas → load `references/messaging-canvas.md` and `assets/messaging-canvas-template.md`

**If the user is doing Evangelist work:**
- Enabling sales with playbook, reference customers, battle cards → `references/partner-collaboration.md` (sales section)
- Community, fandom, analysts → `references/campaigns-beyond-product.md`

When the task touches multiple of these, read the relevant references in parallel before writing a word of output. The book's cross-references are dense; treating each topic in isolation produces shallow answers.

## Worked examples to draw from

These four cases recur throughout the book and are worth pulling into any answer where the pattern fits:

- **Netflix messaging evolution (2009 → 2016).** Shows how homepage messaging changes as the product crosses the adoption curve. See `examples/netflix-messaging-evolution.md`.
- **iPhone adoption lifecycle.** Walks from innovators to laggards with Apple's pricing and distribution moves at each stage. See `examples/iphone-adoption-lifecycle.md`.
- **Pocket vs Instapaper.** The PMM mindset beating the better-known competitor without a PMM in title. See `examples/pocket-gtm-strategy.md`.
- **Expensify vs SAP Concur.** Side-by-side of authentic customer-POV messaging versus product-name-led messaging. See `examples/expensify-vs-concur-messaging.md`.
- **PGTM Canvas filled example.** A worked productivity-app canvas. See `examples/pgtm-canvas-filled-saas.md`.

Quote these accurately when drawing on them. Don't paraphrase the examples into generic abstractions. The specific numbers (Word Internet focus groups, Superhuman's "sorry, not yet" to unfit beta users, the $300 vs $125 Nike sunglasses) are what make the lessons stick.

## How to answer well

Four habits worth forming when answering through this skill.

**One, always start with the customer view.** Lauchengco's canvas process, her messaging process, her market-fit process: each begins by asking what the customer sees, feels, and does. If the user hands you a product deck and asks for messaging, don't write messaging from the deck. Ask what customers in each segment are currently trying to do and where they are stuck. Then write.

**Two, use the CAST filter on any message you produce.** Clear, Authentic, Simple, Tested. If you're writing example copy, audit it against CAST before you show it. If you're critiquing the user's copy, name which of the four it's failing.

**Three, prefer guardrails to checklists.** The PGTM Canvas is a guardrail document. The Messaging Canvas is a guardrail document. Lauchengco's complaint with most marketing plans is that they're activity lists without a line back to strategy. When the user asks for "a marketing plan," you probably want to produce a PGTM first and then a handful of campaigns under it, not a calendar of 47 tactics.

**Four, name the fundamental.** When you answer, make it clear which of the four fundamentals the user's question sits under. This orients them, and it makes gaps obvious: if someone is asking only Storyteller questions for a product that hasn't shipped, they may be skipping Ambassador and Strategist work that should come first.

## Anti-patterns to watch for in your own output

Don't produce a template-generated positioning statement. Lauchengco's Ch 5 warning is that "_____ is the _____ for _____ that _____" outputs are derivative, jargon-filled, and focused on what the company wants to say instead of what customers need to hear. Use her messaging discovery process instead.

Don't list MQLs as a PMM metric. MQLs are a marketing metric. PMM metrics are longer-term: category leadership, win rate vs competition, organic evangelism, CAC trend, NPS as leading retention indicator. If the user asks for "PMM metrics" and you're about to write "MQLs, SQLs, pipeline," stop and read `references/pmm-metrics.md`.

Don't treat a Release Scale or PGTM Canvas as one-shot work. Both are living documents. A canvas filled in once and never revisited is worse than no canvas, because the team thinks alignment exists when it doesn't.

Don't recommend "find a good tagline" or "be bold" as messaging advice. If the advice could apply to any product in any category, Lauchengco would call it out. Be specific about what the segment feels, what is different, what is testable.

Don't default to B2B SaaS framing. The book draws examples from Microsoft Office, iPhone, Netflix, Quizlet, Pocket, Dropbox, Peloton, Zendesk, Workiva, AppOmni, a construction-equipment manufacturer, and an insurance company. Match the user's context.

## Anchor quotes to remember

These recur across the book. Use them when they fit and attribute them clearly.

- "Formulas are input, not output." (Ch 5)
- "Positioning is your long game. Messaging is your short game." (Ch 5)
- "Competition isn't a crowd; it's confirmation." (Ch 24)
- "Pricing is value engineering." (Ch 17)
- "Good product marketing takes time, and measuring its effectiveness does too." (Ch 13)
- "Product marketers are made, not born." (Ch 7)
- "If product is the engine of growth, sales is the gas. Marketing is the gas station. Product marketing is the gas station attendant making sure sales gets tanked up." (Ch 10)
- "What product ships, sales can't sell." (Ch 8, the archetypal partnership failure)

## The three canvases

Three one-page tools recur throughout the book. Each has its own reference file and blank template.

- **Product Go-to-Market Canvas** (Ch 19). Aligns product milestones, marketing strategies, and key activities across quarters, all grounded in the customer/outside environment. Owned by PMM, built in a 3-hour cross-functional kickoff, revised quarterly.
- **Messaging Canvas** (Ch 25). Segments, positioning, key support pillars, areas of value in customer-friendly language, and evidence. Force-constrained to one page so only the highest-priority messages survive.
- **Release Scale** (Ch 12). Tiered release taxonomy (Level 1 through ~5) with customer impact, marketing objectives, resources, and lead times per level. Lets product and GTM teams say "is this a Level 2 or Level 3?" and agree on what that means.

When a user's question would benefit from one of these, don't just recommend they build one. Offer to co-build it with them right now, starting from their context.

## A note on fit with your other PMM skills

This skill coexists with generic PMM skills (messaging-positioning, product-launch-playbook, competitive-battlecard, sales-enablement-assets, pricing-packaging, pmm-workflow, etc.). Prefer this skill when:

- The user names Lauchengco or the book.
- The user wants the specific canvases or the CAST filter.
- The user's question is about PMM-as-a-role (structure, hiring, leadership, career) rather than a tactical deliverable.
- The user's context is early / growth / inflection-point stage where the book's stage guidance applies.

Prefer the other skills when the user needs a polished deliverable in a standard format (a battle card, a launch plan, a one-pager) and the book's method would add ceremony without changing the output. You can still borrow this skill's frames (CAST, PGTM guardrails, fundamentals) while the other skill produces the artifact.
