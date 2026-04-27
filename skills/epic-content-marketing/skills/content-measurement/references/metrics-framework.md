# Content metrics reference

Use this when building measurement plans. Each metric includes a definition, what it signals, and common mistakes in how teams use it.

---

## Layer 1: Consumption metrics

### Pageviews
Definition: Total number of times a page was loaded, including repeat visits by the same user.
What it signals: Overall volume of content discovery. Useful for trending direction, not absolute performance.
Common mistake: Treating a pageview spike from a social post as content success without checking whether those visitors subscribed or returned.

### Unique visitors (also: unique sessions)
Definition: Number of distinct individuals who visited the site in a given period, estimated by cookies/device fingerprinting.
What it signals: Actual reach. More meaningful than raw pageviews.
Common mistake: Not segmenting by source. Organic traffic from search and direct traffic from subscribers tell very different stories.

### Email open rate
Definition: Percentage of delivered emails that were opened (opens ÷ delivered).
What it signals: Subject line quality and subscriber engagement. A consistent 35%+ open rate for a B2B newsletter is healthy. Below 20% is a problem.
Common mistake: Treating Apple Mail open inflation (from Mail Privacy Protection) as real engagement. Look at click rate to confirm engagement.

### Email click rate
Definition: Percentage of delivered emails where at least one link was clicked.
What it signals: Content relevance and CTA quality. More reliable than open rate post-2021.
Common mistake: Averaging click rate across all issues. Break it down by issue to identify which content topics drive action.

### Podcast downloads
Definition: Number of times an episode file was downloaded within 30 days of publish (IAB standard).
What it signals: Episode reach and show growth trend. 1,000+ downloads per episode within 30 days is a meaningful threshold for most niches.
Common mistake: Tracking cumulative downloads (grows indefinitely and means nothing) instead of per-episode 30-day downloads.

### Video views / view duration
Definition: Views = number of times video was played for at least a few seconds (threshold varies by platform). View duration = average percentage of video watched.
What it signals: Views indicate reach; duration indicates content quality. A video with 10,000 views and 15% average view duration is worse than one with 2,000 views and 70%.
Common mistake: Optimizing for view count at the cost of duration. YouTube's algorithm rewards watch time, not raw views.

---

## Layer 2: Sharing metrics

### Social shares
Definition: Number of times a piece of content was shared to social platforms (button clicks or tracked share events).
What it signals: Audience willingness to stake their reputation on the content. Shares are a proxy for quality.
Common mistake: Not distinguishing share types. A share from a respected industry voice is worth more than 50 automated shares.

### Inbound links (backlinks)
Definition: External websites linking to a specific content piece.
What it signals: Authority and content quality, particularly for SEO. Also a measure of whether content is reference-worthy in the industry.
Common mistake: Counting total links without checking link quality. Ten relevant backlinks from industry publications beat 500 from unrelated directories.

### Email forwards
Definition: Tracked via email platform's forward-to-a-friend link. Not counted when subscribers use their email client's native forward button.
What it signals: That subscribers value the content enough to recommend it to colleagues. One of the strongest signals of content quality.
Common mistake: Not offering a deliberate forward prompt in newsletters. If you don't ask readers to forward, fewer will.

---

## Layer 3: Lead generation / subscription metrics

### New email subscribers
Definition: Net new addresses added to the list in a given period.
What it signals: Whether content is building an owned audience. This is the most important metric for most content programs.
Common mistake: Reporting total list size instead of growth rate. A list of 10,000 that added 3 new subscribers last month is a dying program.

### Email list growth rate
Formula: (New subscribers - Unsubscribes - Bounces) ÷ Starting list size × 100
What it signals: Net momentum of the content program. A healthy list grows 2–5% per month. Negative growth rate means the program is losing audience faster than gaining it.
Common mistake: Not accounting for churn. Adding 200 subscribers while losing 250 is net negative even if the raw "new subscriber" number looks good.

### Subscriber source attribution
Definition: Which pieces of content, campaigns, or channels drove new subscribers.
What it signals: Where to invest more. If 60% of subscribers came from one cornerstone article, write more like that article.
Common mistake: Not tracking this at all. Most email platforms support UTM or form-specific tracking. Use it.

### Email unsubscribe rate
Definition: Percentage of subscribers who opt out per email sent (typical benchmark: below 0.3% per send is healthy).
What it signals: Content relevance and list hygiene. A spike after a specific issue means that issue failed or attracted the wrong subscribers.
Common mistake: Treating all unsubscribes as a failure. Some churn is healthy — people who don't want the content are leaving, which improves engagement rates.

### Content-influenced form completions
Definition: Form completions (demo request, trial signup, contact form) where the user also visited specific content pages in the same session or within the attribution window.
What it signals: Whether content is a factor in the decision to engage with the business.
Common mistake: Requiring last-touch attribution. Content rarely converts on the first visit. Use a multi-touch or time-decay attribution model.

---

## Layer 4: Sales metrics

### Content-influenced pipeline
Definition: Value of sales opportunities where the contact engaged with content before or during the sales process. Requires CRM tracking of content touchpoints.
What it signals: Content's contribution to revenue generation. Typically tracked by tagging contacts who subscribed or visited key content pages before the opportunity was created.
Common mistake: Claiming influence for any content visit, no matter how brief. Set a minimum engagement threshold (e.g., 3+ content pages visited, or active email subscriber for 30+ days).

### Content-influenced revenue
Definition: Closed/won revenue from deals where the contact had documented content touchpoints.
What it signals: The dollar value of content in the sales process. This is the strongest argument for content marketing investment.
Common mistake: Confusing content-influenced revenue with content-generated revenue. Content almost never generates revenue directly — it influences a process with many other factors. Overclaiming destroys credibility.

### Time to close: subscribers vs. non-subscribers
Definition: Average sales cycle length for contacts who subscribed to content vs. those who didn't.
What it signals: Whether content accelerates decision-making. If subscribers close 30% faster, the content is doing real work.
Common mistake: Ignoring this metric entirely. It's often the clearest proof of content's role in sales.

### Subscriber retention rate
Definition: Percentage of customers who renew or stay active and who are also active content subscribers.
What it signals: Whether content supports customer success and loyalty.
Common mistake: Not segmenting the customer base by content engagement. The comparison group (non-subscribers) is where the insight lives.

---

## ROO quick reference

| Business goal | Primary ROO metric | Secondary metrics |
|---|---|---|
| Lead generation | Content-influenced leads per month | Subscriber growth rate, form completions |
| Brand awareness | Monthly unique visitors (organic) | Inbound links, share rate |
| Customer retention | Subscriber retention rate vs. non-subscribers | Unsubscribe rate, email engagement |
| Sales support | Time to close (subscribers vs. non) | Content-influenced pipeline |
| Content revenue | Direct revenue from content products | Subscriber growth, conversion rate |

---

## Reporting anti-patterns (what NOT to put in a content report)

- Total followers across all social platforms (aggregated vanity metric)
- Cumulative pageviews since launch (grows forever, tells you nothing about current health)
- Number of content pieces published (output ≠ outcome)
- Sentiment scores without tied actions (unactionable)
- Bounce rate without context (varies widely by content type; a blog post with high bounce but high time-on-page is fine)
- "Reach" from boosted posts (paid reach is not organic reach; mixing them distorts both)
