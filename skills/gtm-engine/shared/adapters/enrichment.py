"""
Optional contact enrichment adapter.

Default: returns contributor or contact info supplied manually by the caller.
No external call, no key needed. The tool always runs fully on manual input.

Optional hooks:
  - Clay (clay.com)       — set CLAY_API_KEY + ENRICHMENT_SOURCE=clay
  - Apollo (apollo.io)    — set APOLLO_API_KEY + ENRICHMENT_SOURCE=apollo
  - CRM CSV export        — set ENRICHMENT_SOURCE=csv, CRM_EXPORT_PATH=path/to/export.csv

Usage:
    from shared.adapters.enrichment import enrich_contact

    # Manual default:
    contact = enrich_contact({"name": "Ada Lovelace", "company": "Acme", "url": "..."})
    # Returns the same dict, possibly supplemented if a paid source is configured.
"""

import csv
import os
from pathlib import Path


def enrich_contact(contact: dict) -> dict:
    """
    Enrich a contact record. Returns a dict with the same keys as input,
    plus any additional fields the active source can supply.

    Always returns something — never blocks on a missing key.

    Args:
        contact: A dict with at least {"name": str, "company": str}.
                 May also include "url", "email", "title", "linkedin_url", etc.
    """
    source = os.environ.get("ENRICHMENT_SOURCE", "").lower()

    if source == "clay":
        return _enrich_clay(contact)
    elif source == "apollo":
        return _enrich_apollo(contact)
    elif source == "csv":
        return _enrich_csv(contact)
    else:
        # Manual default — return as-is, log once if no source is configured
        _warn_once()
        return contact


def enrich_contacts(contacts: list[dict]) -> list[dict]:
    """Batch-enrich a list of contact dicts."""
    return [enrich_contact(c) for c in contacts]


# ── Optional enrichment hooks ─────────────────────────────────────────────────
# TODO: implement by setting the appropriate env vars and installing the SDK.

def _enrich_clay(contact: dict) -> dict:
    # TODO: set CLAY_API_KEY and ENRICHMENT_SOURCE=clay to activate.
    # Clay API docs: https://docs.clay.com
    key = os.environ.get("CLAY_API_KEY")
    if not key:
        print("[enrichment] Clay skipped: CLAY_API_KEY not set.")
        return contact
    print("[enrichment] Clay adapter not yet implemented. Returning manual data.")
    return contact


def _enrich_apollo(contact: dict) -> dict:
    # TODO: set APOLLO_API_KEY and ENRICHMENT_SOURCE=apollo to activate.
    # Apollo API docs: https://apolloio.github.io/apollo-api-docs/
    key = os.environ.get("APOLLO_API_KEY")
    if not key:
        print("[enrichment] Apollo skipped: APOLLO_API_KEY not set.")
        return contact
    print("[enrichment] Apollo adapter not yet implemented. Returning manual data.")
    return contact


def _enrich_csv(contact: dict) -> dict:
    # TODO: Export your CRM to CSV and set:
    #   ENRICHMENT_SOURCE=csv
    #   CRM_EXPORT_PATH=path/to/crm_export.csv
    # The CSV must have a column matching on 'email' or 'name'+'company'.
    export_path = os.environ.get("CRM_EXPORT_PATH")
    if not export_path:
        print("[enrichment] CSV enrichment skipped: CRM_EXPORT_PATH not set.")
        return contact

    path = Path(export_path)
    if not path.exists():
        print(f"[enrichment] CSV file not found: {export_path}")
        return contact

    try:
        with path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if _matches(contact, row):
                    merged = dict(row)
                    merged.update({k: v for k, v in contact.items() if v})
                    return merged
    except Exception as exc:
        print(f"[enrichment] CSV read error: {exc}")

    return contact


def _matches(contact: dict, row: dict) -> bool:
    """Return True if a CSV row matches the contact on email or name+company."""
    email = (contact.get("email") or "").lower().strip()
    if email and email == (row.get("email") or "").lower().strip():
        return True
    name = (contact.get("name") or "").lower().strip()
    company = (contact.get("company") or "").lower().strip()
    row_name = (row.get("name") or "").lower().strip()
    row_company = (row.get("company") or "").lower().strip()
    return bool(name and company and name == row_name and company == row_company)


_warned = False


def _warn_once() -> None:
    global _warned
    if not _warned:
        print(
            "[enrichment] Using manual data (no ENRICHMENT_SOURCE set). "
            "To add enrichment: set ENRICHMENT_SOURCE=clay|apollo|csv."
        )
        _warned = True
