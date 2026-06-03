"""
Render a self-contained HTML report with inline CSS.

Usage:
    from shared.report import render, Section

    html = render(
        title="Entity Audit: Acme Corp",
        sections=[
            Section("Score", "<p>72 / 100</p>"),
            Section("Gaps", "<ul><li>Missing Wikidata entry</li></ul>"),
        ],
    )
    Path("report.html").write_text(html)

Each Section has a heading and HTML body (strings). Callers are responsible
for escaping any user-supplied text before passing it in.
"""

import html as _html
from dataclasses import dataclass, field


@dataclass
class Section:
    title: str
    content: str          # raw HTML; caller must escape user data
    subsections: list["Section"] = field(default_factory=list)


def render(title: str, sections: list[Section], subtitle: str = "") -> str:
    """Return a complete self-contained HTML document as a string."""
    sections_html = "\n".join(_render_section(s, level=2) for s in sections)
    subtitle_html = f'<p class="subtitle">{_h(subtitle)}</p>' if subtitle else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_h(title)}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 16px;
    line-height: 1.6;
    color: #1a1a1a;
    background: #f8f8f6;
    padding: 2rem 1rem;
  }}

  .page {{
    max-width: 860px;
    margin: 0 auto;
    background: #fff;
    border-radius: 6px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
    overflow: hidden;
  }}

  header {{
    background: #1a1a2e;
    color: #fff;
    padding: 2rem 2.5rem;
  }}

  header h1 {{
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }}

  .subtitle {{
    margin-top: .4rem;
    font-size: .95rem;
    color: #a0a8c0;
  }}

  .toc {{
    background: #f3f3f0;
    border-bottom: 1px solid #e8e8e4;
    padding: 1rem 2.5rem;
  }}

  .toc h2 {{
    font-size: .75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: #666;
    margin-bottom: .5rem;
  }}

  .toc ol {{
    list-style: decimal;
    padding-left: 1.2rem;
  }}

  .toc li {{ margin: .2rem 0; font-size: .9rem; }}
  .toc a {{ color: #2a6dd9; text-decoration: none; }}
  .toc a:hover {{ text-decoration: underline; }}

  .content {{ padding: 2rem 2.5rem; }}

  section {{ margin-bottom: 2.5rem; }}
  section:last-child {{ margin-bottom: 0; }}

  h2 {{
    font-size: 1.15rem;
    font-weight: 700;
    color: #1a1a2e;
    border-bottom: 2px solid #e8e8e4;
    padding-bottom: .4rem;
    margin-bottom: 1rem;
  }}

  h3 {{
    font-size: 1rem;
    font-weight: 600;
    color: #333;
    margin: 1.2rem 0 .5rem;
  }}

  p {{ margin-bottom: .8rem; }}

  ul, ol {{
    padding-left: 1.4rem;
    margin-bottom: .8rem;
  }}

  li {{ margin: .3rem 0; }}

  pre {{
    background: #f3f3f0;
    border: 1px solid #e0e0da;
    border-radius: 4px;
    padding: 1rem;
    overflow-x: auto;
    font-family: "SF Mono", "Fira Mono", Consolas, monospace;
    font-size: .85rem;
    line-height: 1.5;
    margin-bottom: 1rem;
  }}

  code {{
    font-family: "SF Mono", "Fira Mono", Consolas, monospace;
    font-size: .875em;
    background: #f0f0ec;
    padding: .1em .3em;
    border-radius: 3px;
  }}

  pre code {{ background: none; padding: 0; font-size: inherit; }}

  table {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
    font-size: .9rem;
  }}

  th {{
    text-align: left;
    background: #f3f3f0;
    border-bottom: 2px solid #d8d8d4;
    padding: .5rem .75rem;
    font-weight: 600;
  }}

  td {{
    padding: .45rem .75rem;
    border-bottom: 1px solid #ebebeb;
    vertical-align: top;
  }}

  tr:last-child td {{ border-bottom: none; }}

  .score-badge {{
    display: inline-block;
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a2e;
    background: #f3f3f0;
    border-radius: 6px;
    padding: .3rem .8rem;
    margin-bottom: .8rem;
  }}

  .tag {{
    display: inline-block;
    font-size: .75rem;
    font-weight: 600;
    padding: .15rem .5rem;
    border-radius: 3px;
    margin: .15rem .1rem;
  }}

  .tag-hot  {{ background: #fee2e2; color: #991b1b; }}
  .tag-warm {{ background: #fef3c7; color: #92400e; }}
  .tag-cool {{ background: #dbeafe; color: #1e40af; }}
  .tag-ok   {{ background: #d1fae5; color: #065f46; }}
  .tag-gap  {{ background: #fce7f3; color: #9d174d; }}

  .notice {{
    background: #fffbeb;
    border-left: 4px solid #f59e0b;
    padding: .75rem 1rem;
    margin-bottom: 1rem;
    font-size: .9rem;
    border-radius: 0 4px 4px 0;
  }}

  footer {{
    text-align: center;
    font-size: .8rem;
    color: #999;
    padding: 1.2rem;
    border-top: 1px solid #ebebeb;
  }}
</style>
</head>
<body>
<div class="page">

<header>
  <h1>{_h(title)}</h1>
  {subtitle_html}
</header>

{_render_toc(sections)}

<div class="content">
{sections_html}
</div>

<footer>Generated by gtm-engine &mdash; open this file in any browser, no server needed.</footer>
</div>
</body>
</html>"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _h(text: str) -> str:
    """HTML-escape plain text for use in attributes or text nodes."""
    return _html.escape(text)


def _slug(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _render_toc(sections: list[Section]) -> str:
    if not sections:
        return ""
    items = "\n".join(
        f'  <li><a href="#{_slug(s.title)}">{_h(s.title)}</a></li>'
        for s in sections
    )
    return f"""<nav class="toc">
<h2>Contents</h2>
<ol>
{items}
</ol>
</nav>"""


def _render_section(section: Section, level: int = 2) -> str:
    tag = f"h{level}"
    sid = _slug(section.title)
    sub_html = "\n".join(_render_section(s, level=level + 1) for s in section.subsections)
    return f"""<section id="{sid}">
<{tag}>{_h(section.title)}</{tag}>
{section.content}
{sub_html}
</section>"""
