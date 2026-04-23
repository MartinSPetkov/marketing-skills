# Martin's Marketing Skills Collection

A personal library of skills for Claude. Each skill is a `.skill` file you can install directly into Claude to extend what it knows how to do.

Skills work by giving Claude a detailed reference document to consult when you ask it something relevant. Instead of relying on general training, Claude reads the skill and follows its specific instructions, frameworks, and examples.

## How to install a skill/plugin

1. Navigate to the skill folder (e.g., `marketing-leadership`)
2. Copy the `.md` or `.skill` or `.plugin` file and any files in the `references/` folder
3. Go to [claude.ai](https://claude.ai) and open Customize 
4. Navigate to Skills or Plugins (only works on desktop)
5. Upload the `.md` or `.skill` or `.plugin` file and reference files

The skill/plugin is now active in your conversations.

---

## Marketing Skills

### [`marketing-leadership`](./skills/marketing-leadership)

Based on *The 12 Powers of a Marketing Leader* by Thomas Barta and Patrick Barwise, drawing on a global study of 1,232 senior marketers and 100+ CMO interviews. Gives Claude the V-Zone framework, the three marketing-specific gaps (trust, power, skills), and the 12 Powers across four challenges: mobilizing your boss, your colleagues, your team, and yourself. Includes a 7-question diagnostic and practical actions for each Power.

Good for senior marketers working on C-suite influence, team performance, or their own leadership development.

### [`loved-pmm`](./skills/loved-pmm)

Based on *Loved: How to Rethink Marketing for Tech Products* by Martina Lauchengco (Wiley, 2022). Encodes her PMM methods: the Four Fundamentals (Ambassador, Strategist, Storyteller, Evangelist), the Product Go-to-Market Canvas, the Messaging Canvas, the Release Scale, and the CAST filter. Ships with blank templates, five worked examples (Netflix, iPhone, Pocket, Expensify vs Concur, a filled SaaS PGTM), and an anti-patterns index.

Good for PMMs doing messaging audits, positioning, launch tiering, pricing, hiring, or org design. PMM leaders dealing with "what product ships, sales can't sell"-style partnership breakdowns.

### [`obviously-awesome`](./skills/obviously-awesome)

Based on *Obviously Awesome* by April Dunford. A practical set of positioning tools: the Positioning Canvas, a Positioning Audit, a Positioning Workshop flow, Competitive Alternatives mapping, Unique Value mapping, Market Framing, and a Sales Story builder—each with prompts and evals.

Good for founders/PMMs doing positioning refreshes, competitive narrative work, sales enablement, and category/market context decisions.

---

## Other Useful Skills

### [AI Marketing Skills by Eric Osiu](https://github.com/ericosiu/ai-marketing-skills)

A collection of complete marketing and sales automation workflows for Claude Code. Includes 15+ skill categories covering growth experiments, sales pipeline automation, content operations, SEO optimization, and financial analysis.

### [Marketing Skills by Corey Haines](https://github.com/coreyhaines31/marketingskills)

A comprehensive library of AI agent skills for marketing tasks including conversion optimization, copywriting, SEO, analytics, and growth engineering. Designed to work with Claude Code, Cursor, and other AI coding agents for landing page optimization, email campaigns, paid advertising, and sales enablement.

---

## About

These skills are built from books, frameworks, and research I find genuinely useful in my work as a senior marketing professional. Each one is an attempt to make a body of knowledge actually usable inside Claude, not just stored somewhere.

If you use any of these and have feedback, feel free to open an issue.