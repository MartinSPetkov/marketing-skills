# entity_auditor samples

This tool runs live on real public URLs. There is no synthetic sample data.

See `entity_auditor_targets.md` in the repo root for suggested demo targets.

Good choices for demo:
- A B2B SaaS prospect with a clear entity gap (no Wikidata entry, thin Organization schema).
- Run on two or three sites beforehand; demo the one with the most visible gap.
- Catalyst itself (gotcatalyst.com) is a bold option — it shows you came with a finding.

Run command:

    python entity_auditor/entity_audit.py --brand "Acme" --url "https://acme.com"
