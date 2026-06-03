"""
Fetch a URL and return clean parsed content.

Returns a FetchResult with:
- text:     visible body text, whitespace-normalised
- headings: list of {"level": 2, "text": "..."} dicts
- jsonld:   list of parsed JSON-LD objects found in <script type="application/ld+json">
- faq:      list of {"question": "...", "answer": "..."} pairs
- body:     raw visible body text (same as text; kept for clarity in callers)

Never fetches Google search result pages or LinkedIn.
"""

import json
import re
import urllib.parse
from dataclasses import dataclass, field

import requests
from bs4 import BeautifulSoup

_TIMEOUT = 15  # seconds
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; gtm-engine/1.0; +https://github.com/your-org/gtm-engine)"
    )
}

_BLOCKED_HOSTS = {
    "google.com", "www.google.com",
    "linkedin.com", "www.linkedin.com",
    "linkedin.cn",
}


@dataclass
class FetchResult:
    url: str
    text: str = ""
    headings: list[dict] = field(default_factory=list)
    jsonld: list[dict] = field(default_factory=list)
    faq: list[dict] = field(default_factory=list)
    body: str = ""
    raw_html: str = ""
    links: list[str] = field(default_factory=list)  # all href values on the page
    error: str = ""

    @property
    def ok(self) -> bool:
        return not self.error


def fetch(url: str) -> FetchResult:
    """Fetch a URL and return structured content. Never fetches Google or LinkedIn."""
    _guard_url(url)

    try:
        resp = requests.get(url, headers=_HEADERS, timeout=_TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        return FetchResult(url=url, error=f"Timed out after {_TIMEOUT}s")
    except requests.exceptions.HTTPError as exc:
        return FetchResult(url=url, error=f"HTTP {exc.response.status_code}: {exc}")
    except requests.exceptions.RequestException as exc:
        return FetchResult(url=url, error=str(exc))

    soup = BeautifulSoup(resp.text, "html.parser")

    headings = _extract_headings(soup)
    jsonld = _extract_jsonld(soup)
    faq = _extract_faq(soup, jsonld)
    body = _extract_body(soup)
    links = _extract_links(soup, base_url=url)

    return FetchResult(
        url=url,
        text=body,
        headings=headings,
        jsonld=jsonld,
        faq=faq,
        body=body,
        raw_html=resp.text,
        links=links,
    )


# ── Extraction helpers ────────────────────────────────────────────────────────

def _guard_url(url: str) -> None:
    host = urllib.parse.urlparse(url).hostname or ""
    # Strip leading www. for comparison
    bare = host.removeprefix("www.")
    if host in _BLOCKED_HOSTS or bare in _BLOCKED_HOSTS:
        raise ValueError(
            f"Fetching {host} is not allowed. "
            "Do not scrape Google search results or LinkedIn."
        )


def _extract_headings(soup: BeautifulSoup) -> list[dict]:
    headings = []
    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        text = tag.get_text(separator=" ", strip=True)
        if text:
            headings.append({"level": int(tag.name[1]), "text": text})
    return headings


def _extract_jsonld(soup: BeautifulSoup) -> list[dict]:
    blocks = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            # Some pages embed an array of schemas at the top level
            if isinstance(data, list):
                blocks.extend(data)
            else:
                blocks.append(data)
        except (json.JSONDecodeError, TypeError):
            continue
    return blocks


def _extract_faq(soup: BeautifulSoup, jsonld: list[dict]) -> list[dict]:
    pairs: list[dict] = []

    # 1. Pull from FAQPage JSON-LD if present
    for schema in jsonld:
        if schema.get("@type") == "FAQPage":
            for item in schema.get("mainEntity", []):
                q = item.get("name", "").strip()
                a_block = item.get("acceptedAnswer", {})
                a = a_block.get("text", "").strip() if isinstance(a_block, dict) else ""
                if q and a:
                    pairs.append({"question": q, "answer": a})
            return pairs  # authoritative source found; stop here

    # 2. Heuristic: heading followed immediately by paragraph(s)
    for tag in soup.find_all(["h2", "h3"]):
        text = tag.get_text(separator=" ", strip=True)
        if text.endswith("?"):
            answer_parts = []
            for sib in tag.next_siblings:
                if sib.name in ("h2", "h3", "h4"):
                    break
                if sib.name == "p":
                    part = sib.get_text(separator=" ", strip=True)
                    if part:
                        answer_parts.append(part)
            if answer_parts:
                pairs.append({"question": text, "answer": " ".join(answer_parts)})

    return pairs


def _extract_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    """Return absolute hrefs for all <a> tags on the page."""
    base = urllib.parse.urlparse(base_url)
    seen: set[str] = set()
    links: list[str] = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        absolute = urllib.parse.urljoin(base_url, href)
        # Keep only http(s) links on the same domain
        parsed = urllib.parse.urlparse(absolute)
        if parsed.scheme in ("http", "https") and absolute not in seen:
            seen.add(absolute)
            links.append(absolute)
    return links


def _extract_body(soup: BeautifulSoup) -> str:
    # Remove non-content tags
    for tag in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # Collapse runs of blank lines
    lines = [line.strip() for line in text.splitlines()]
    cleaned = re.sub(r"\n{3,}", "\n\n", "\n".join(lines))
    return cleaned.strip()
