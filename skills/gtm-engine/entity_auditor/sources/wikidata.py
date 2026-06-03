"""
Wikidata entity lookup for entity_auditor.

Uses the free public Wikidata API — no key, no scraping.
Returns a WikidataResult describing whether the brand has a Wikidata entity
and what signals that entity carries.

To add more sources, create a new module here (e.g. sources/opencorporates.py)
following the same pattern: a single lookup function returning a dataclass.
"""

from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass, field

import requests

_API = "https://www.wikidata.org/w/api.php"
_TIMEOUT = 10

# Wikidata's API policy requires a descriptive User-Agent with contact info.
# https://www.mediawiki.org/wiki/API:Etiquette
_HEADERS = {
    "User-Agent": "gtm-engine/1.0 (entity-authority-auditor; https://github.com/your-org/gtm-engine) python-requests/2.x"
}

# Property IDs we care about
_PROP_WEBSITE = "P856"
_PROP_TWITTER = "P2002"
_PROP_LINKEDIN_ORG = "P4264"
_PROP_FACEBOOK = "P2013"
_PROP_INDUSTRY = "P452"
_PROP_FOUNDED = "P571"
_PROP_COUNTRY = "P17"
_PROP_EMPLOYEES = "P1128"
_PROP_CRUNCHBASE = "P2088"
_PROP_GITHUB = "P9001"


@dataclass
class WikidataResult:
    found: bool = False
    entity_id: str = ""
    entity_url: str = ""
    label: str = ""
    description: str = ""
    aliases: list[str] = field(default_factory=list)
    website: str = ""
    twitter: str = ""
    linkedin: str = ""
    facebook: str = ""
    industry: str = ""
    founded: str = ""
    country: str = ""
    crunchbase_id: str = ""
    github: str = ""
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error

    def same_as_urls(self) -> list[str]:
        """Return all verified external URLs for sameAs use."""
        urls = []
        if self.entity_url:
            urls.append(self.entity_url)
        if self.twitter:
            urls.append(f"https://twitter.com/{self.twitter}")
        if self.facebook:
            urls.append(f"https://www.facebook.com/{self.facebook}")
        if self.crunchbase_id:
            urls.append(f"https://www.crunchbase.com/organization/{self.crunchbase_id}")
        return urls

    def summary(self) -> dict:
        return {
            "found": self.found,
            "entity_id": self.entity_id,
            "entity_url": self.entity_url,
            "label": self.label,
            "description": self.description,
            "aliases": self.aliases,
            "website": self.website,
            "twitter": self.twitter,
            "linkedin": self.linkedin,
            "industry": self.industry,
            "founded": self.founded,
            "country": self.country,
            "crunchbase_id": self.crunchbase_id,
            "same_as_urls": self.same_as_urls(),
        }


def lookup(brand_name: str, homepage_url: str = "") -> WikidataResult:
    """
    Search Wikidata for the brand and return a WikidataResult.
    Picks the best match; prefers entities whose website matches homepage_url.
    """
    try:
        candidates = _search(brand_name)
    except Exception as exc:
        return WikidataResult(error=f"Wikidata search failed: {exc}")

    if not candidates:
        return WikidataResult(found=False)

    # Pick the best candidate: prefer one whose P856 (website) matches homepage_url
    best_id = _pick_best(candidates, homepage_url)
    if not best_id:
        return WikidataResult(found=False)

    try:
        return _get_entity(best_id)
    except Exception as exc:
        return WikidataResult(error=f"Wikidata entity fetch failed: {exc}")


# ── Internal ──────────────────────────────────────────────────────────────────

def _search(query: str) -> list[str]:
    """Return a list of entity QIDs matching query."""
    params = {
        "action": "wbsearchentities",
        "search": query,
        "language": "en",
        "format": "json",
        "type": "item",
        "limit": "7",
    }
    resp = requests.get(_API, params=params, headers=_HEADERS, timeout=_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return [item["id"] for item in data.get("search", [])]


def _pick_best(qids: list[str], homepage_url: str) -> str:
    """
    Return the QID whose official website best matches homepage_url.
    Falls back to the first result if no website match is found.
    """
    if not qids:
        return ""
    if not homepage_url:
        return qids[0]

    home_host = _host(homepage_url)

    # Batch-fetch website claims for all candidates
    ids_param = "|".join(qids)
    params = {
        "action": "wbgetentities",
        "ids": ids_param,
        "format": "json",
        "props": "claims",
        "languages": "en",
    }
    try:
        resp = requests.get(_API, params=params, headers=_HEADERS, timeout=_TIMEOUT)
        resp.raise_for_status()
        entities = resp.json().get("entities", {})
    except Exception:
        return qids[0]

    for qid in qids:
        entity = entities.get(qid, {})
        for claim in entity.get("claims", {}).get(_PROP_WEBSITE, []):
            try:
                url = claim["mainsnak"]["datavalue"]["value"]
                if _host(url) == home_host:
                    return qid
            except (KeyError, TypeError):
                continue

    return qids[0]


def _get_entity(qid: str) -> WikidataResult:
    """Fetch full entity data for a QID."""
    params = {
        "action": "wbgetentities",
        "ids": qid,
        "format": "json",
        "languages": "en",
        "props": "labels|descriptions|aliases|claims",
    }
    resp = requests.get(_API, params=params, headers=_HEADERS, timeout=_TIMEOUT)
    resp.raise_for_status()
    entity = resp.json().get("entities", {}).get(qid, {})

    label = _en_value(entity.get("labels", {}))
    description = _en_value(entity.get("descriptions", {}))
    aliases = [
        a["value"]
        for a in entity.get("aliases", {}).get("en", [])
    ]

    claims = entity.get("claims", {})
    website = _string_claim(claims, _PROP_WEBSITE)
    twitter = _string_claim(claims, _PROP_TWITTER)
    linkedin = _string_claim(claims, _PROP_LINKEDIN_ORG)
    facebook = _string_claim(claims, _PROP_FACEBOOK)
    crunchbase = _string_claim(claims, _PROP_CRUNCHBASE)
    github = _string_claim(claims, _PROP_GITHUB)
    industry = _item_label(claims, _PROP_INDUSTRY)
    founded = _time_claim(claims, _PROP_FOUNDED)
    country = _item_label(claims, _PROP_COUNTRY)

    return WikidataResult(
        found=True,
        entity_id=qid,
        entity_url=f"https://www.wikidata.org/wiki/{qid}",
        label=label,
        description=description,
        aliases=aliases,
        website=website,
        twitter=twitter,
        linkedin=linkedin,
        facebook=facebook,
        industry=industry,
        founded=founded,
        country=country,
        crunchbase_id=crunchbase,
        github=github,
    )


# ── Claim extractors ──────────────────────────────────────────────────────────

def _en_value(lang_map: dict) -> str:
    return lang_map.get("en", {}).get("value", "")


def _string_claim(claims: dict, prop: str) -> str:
    for claim in claims.get(prop, []):
        try:
            val = claim["mainsnak"]["datavalue"]["value"]
            if isinstance(val, str):
                return val.strip()
        except (KeyError, TypeError):
            continue
    return ""


def _time_claim(claims: dict, prop: str) -> str:
    for claim in claims.get(prop, []):
        try:
            val = claim["mainsnak"]["datavalue"]["value"]["time"]
            # Format: +2015-01-01T00:00:00Z — extract year
            match = re.search(r"\+?(\d{4})", val)
            return match.group(1) if match else val
        except (KeyError, TypeError):
            continue
    return ""


def _item_label(claims: dict, prop: str) -> str:
    """For claims that point to another Wikidata item, return the item ID (label lookup skipped for speed)."""
    for claim in claims.get(prop, []):
        try:
            val = claim["mainsnak"]["datavalue"]["value"]
            if isinstance(val, dict) and "id" in val:
                return val["id"]
        except (KeyError, TypeError):
            continue
    return ""


def _host(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    return (parsed.hostname or "").removeprefix("www.").lower()
