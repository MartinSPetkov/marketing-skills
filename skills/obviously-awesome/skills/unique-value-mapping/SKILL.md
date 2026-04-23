---
name: obviously-awesome:unique-value-mapping
description: "Map a product's unique attributes to customer value themes, then identify which customer characteristics predict high affinity for that value. This is Steps 5, 6, and 7 of the Dunford positioning process. Use when a team knows their competitive alternatives but hasn't translated features into customer value, when the product has many features but the team can't articulate why they matter, when different customer segments seem to value the product differently and the team wants to understand why, or when positioning claims are vague ('powerful', 'easy', 'comprehensive') and need grounding. Trigger phrases: 'map our features to value', 'what value do we deliver', 'why do customers care about our features', 'value themes', 'Dunford Steps 5 6 7', 'feature to benefit to value', 'who cares most about what we do', 'segmentation based on value', 'unique attributes'. Requires competitive alternatives to be defined first."
---

# Unique Value Mapping (Steps 5–7)

This skill executes Steps 5, 6, and 7 of April Dunford's positioning process: isolating unique attributes, mapping them to customer value, and identifying who cares most about that value.

## Prerequisites

Competitive alternatives (Step 4) must be defined before running this skill. Attributes are only "unique" relative to specific alternatives. Without knowing what customers compare you to, you cannot know what is genuinely different about your product.

If competitive alternatives are not yet defined, use the `competitive-alternatives` skill first.

## Step 5: Isolate unique attributes

### What counts as a unique attribute

A unique attribute is something the product or company has or does that the competitive alternatives do not have or do. Compare only against the alternatives the best-fit customers actually see — not the entire universe of possible competitors.

Categories to explore:

- **Technical features:** algorithms, integrations, performance specs, data models, processing speeds, patented capabilities
- **Delivery or implementation model:** self-serve vs. high-touch onboarding, API-first vs. GUI-only, hosted vs. on-premise, async vs. real-time
- **Business model:** how it's priced vs. alternatives (per-seat vs. usage-based, transaction fee vs. subscription, outcome-based vs. flat fee)
- **Team expertise:** certifications, domain knowledge, customer base composition that creates network effects or learning
- **Partnerships and ecosystem:** integrations, certifications, or co-sell arrangements the alternatives lack
- **Data or network effects:** advantages that grow as more customers use the product

### How to run this step

Ask the user: "Given the competitive alternatives we identified, list everything your product or company has or does that those alternatives do not."

Be expansive. Do not evaluate importance yet. Include things that:
- Some team members might consider weaknesses (mandatory implementation fees, no mobile app)
- Seem obvious to the team but might not be obvious to customers
- Are difficult to prove yet but are real capabilities

**Capturing proof:** For each claimed attribute, ask how it can be proven to a skeptical prospect. Anecdotal claims ("we have great customer support") do not count without evidence. What third-party validation, measurable metric, or customer quote backs it up? Mark unproven claims as [NEEDS PROOF].

### Output

A comprehensive list of unique attributes with proof notes. Do not rank or select yet.

---

## Step 6: Map attributes to value themes

### The three-level translation

Move every attribute through this sequence:

| Level | Definition | Example |
|---|---|---|
| Feature | Something the product does or has | Patented fuzzy logic query algorithm |
| Benefit | What the feature enables | Queries execute faster |
| Value | How this maps to a customer goal | Analysts get answers in real time during customer calls, reducing callback rates and improving satisfaction |

The feature describes what it is. The benefit describes what it does. The value describes what the customer can accomplish because of it — in their terms, tied to something they actually care about.

**Common errors at this step:**
- Stopping at "benefit" and calling it value. "Faster queries" is a benefit. The customer goal it serves (no callbacks, better customer conversations) is the value.
- Writing value claims in internal language the customer wouldn't use. Test every value statement: "Would a customer say this in their own words?"
- Claiming value without proof. Quantify wherever possible (saves 10 hours/week, reduces cost by $50,000/year, cuts response time from 3 days to 4 hours).

### Clustering into value themes

After building the feature/benefit/value table, group related attributes. Ask: "What would be naturally related in the minds of customers? What attributes together deliver one coherent thing the customer can do?"

Aim for 1–4 value themes. More than four suggests the positioning is trying to be too many things. One value theme can be powerful — it focuses everything.

Examples of valid value theme names:
- "Real-time analysis at enterprise scale"
- "Deploy without IT involvement"
- "Compliance-ready for regulated industries"
- "Purpose-built for investment banking workflows"

Each theme gets a name, the supporting attributes, the customer value statement (with proof), and the customer goal it serves.

---

## Step 7: Determine who cares a lot

### The segmentation question

Not all customers value all things equally. The attributes that make one customer love a product may be irrelevant to another. Useful segmentation is not demographic ("small businesses") — it is behavioral and contextual: what is it about a customer that makes them care deeply about this specific value?

For each value theme, ask:
- Who has the most acute version of the problem this solves?
- Who has failed to solve this with the primary competitive alternative and is frustrated by that failure?
- Who would pay a premium to have this solved and why?
- What organizational, industry, or situation-based characteristics identify these customers?

### Characteristics worth surfacing

For B2B products, consider:
- **Industry vertical** — regulated industries (fintech, healthcare, legal) often have distinct needs
- **Company growth stage** — rapidly scaling companies have different friction than stable ones
- **Internal team structure** — does the customer have an IT team? A data science function? A compliance team?
- **Regulatory environment** — GDPR, SOC 2, HIPAA, PCI compliance requirements
- **Existing tech stack** — what they've already bought shapes what they need to integrate with
- **Volume or scale** — number of invoices sent, number of employees, amount of data, transaction frequency
- **Triggering events** — headcount crossing a threshold, a recent compliance failure, an acquisition, a new competitive threat

### The best-fit customer validation

Use the best-fit customer list from Step 1 as the validation test. Ask: do the characteristics identified here match those customers? If not, there is a gap — either the value themes are wrong or the segmentation criteria are wrong.

Also ask: are there enough customers with these characteristics to meet near-term revenue goals? If the segment is too small, either the value themes need to broaden or the criteria need loosening.

---

## Output format

Deliver:

**1. Unique attributes list**

| Attribute | Proof available? |
|---|---|
| [attribute 1] | Yes — [source] / No — [NEEDS PROOF] |

**2. Feature/benefit/value table**

| Feature | Benefit | Value (customer goal) |
|---|---|---|
| [feature] | [benefit] | [value in customer terms] |

**3. Value themes**

For each theme (1–4 total):
```
Theme name: [name]
Supporting attributes: [list]
Customer value: [what customers can do]
Proof: [data, quotes, or third-party validation]
Customer goal served: [the underlying job this helps with]
```

**4. Who cares a lot**

For each value theme, 3–5 customer characteristics that predict high affinity:
```
Theme: [theme name]
Who cares most:
- [characteristic 1]
- [characteristic 2]
- [characteristic 3]
Evidence: [from best-fit customer patterns]
```

---

## What comes next

Value themes and "who cares a lot" are the direct inputs to Step 8 (market frame selection). The market frame you choose should put the value themes at the center and make them obvious to the customers who care most. Take the output of this skill directly into the `market-frame` skill.
