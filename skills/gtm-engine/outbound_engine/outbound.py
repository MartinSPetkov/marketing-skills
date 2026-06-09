"""
Outbound Engine — signal-to-meeting engine for inbound engagement.

Turns people who engaged with LinkedIn posts into scored leads, drafts a
personalized multi-touch sequence for each, and books a meeting when a
positive reply is detected. Runs fully offline in dry-run.

Usage
-----
python outbound_engine/outbound.py run \\
    --config outbound_engine/samples/outbound_config.md \\
    --posts outbound_engine/samples/posts.csv \\
    --engagements outbound_engine/samples/engagements.csv \\
    --replies outbound_engine/samples/replies_fixture.csv \\
    --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from shared.antislop import clean
from shared.llm import query_json, query_text
from shared.scoring import score_fit_batch
from shared.sequence import SequenceState, make_ics, simulate_dry_run


# ── Config parsing ─────────────────────────────────────────────────────────────

def load_config(path: str) -> dict:
    text = Path(path).read_text()
    cfg: dict = {"raw": text}

    def _extract(label: str, default: str = "") -> str:
        m = re.search(rf"{re.escape(label)}\s*[:\-]\s*(.+)", text, re.IGNORECASE)
        return m.group(1).strip() if m else default

    cfg["sender_name"]    = _extract("Name")
    cfg["sender_company"] = _extract("Company")
    cfg["sender_offer"]   = _extract("Offer")
    cfg["booking_link"]   = _extract("Booking link")
    cfg["fit_weight"]     = float(_extract("Fit weight", "0.5"))
    cfg["intent_weight"]  = float(_extract("Intent weight", "0.5"))

    hot_m  = re.search(r"Hot\s*[>=]+\s*(\d+)", text, re.IGNORECASE)
    warm_m = re.search(r"Warm\s+(\d+)\s+to\s+(\d+)", text, re.IGNORECASE)
    cfg["hot_threshold"] = int(hot_m.group(1))  if hot_m  else 80
    cfg["warm_low"]      = int(warm_m.group(1)) if warm_m else 60
    cfg["warm_high"]     = int(warm_m.group(2)) if warm_m else 79

    cap_x = re.search(r"Connection requests per day\s*[:\-]\s*(\d+)", text, re.IGNORECASE)
    cap_m = re.search(r"Messages per day\s*[:\-]\s*(\d+)", text, re.IGNORECASE)
    cfg["caps"] = {
        "comments":    0,
        "connections": int(cap_x.group(1)) if cap_x else 25,
        "messages":    int(cap_m.group(1)) if cap_m else 40,
    }

    # Sequence day offsets (outbound has no warmup touch)
    cfg["sequence_def"] = {
        "warmup":          -1,   # not used
        "connection_sent":  0,
        "msg1":             1,
        "msg2":             4,
        "email":            8,
    }

    icp_m = re.search(r"##\s*ICP\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL | re.IGNORECASE)
    cfg["icp_text"] = icp_m.group(1).strip() if icp_m else text

    return cfg


# ── CSV loaders ────────────────────────────────────────────────────────────────

def load_posts(path: str) -> dict[str, dict]:
    posts: dict[str, dict] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            posts[row["post_id"]] = {k: (v or "").strip() for k, v in row.items()}
    return posts


def load_engagements(path: str) -> list[dict]:
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows.append({k: (v or "").strip() for k, v in row.items()})
    return rows


def load_replies(path: str) -> dict[str, dict]:
    replies: dict[str, dict] = {}
    if not path or not Path(path).exists():
        return replies
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = (row.get("name") or "").strip()
            if name:
                replies[name] = {
                    "touch":      (row.get("touch") or "").strip(),
                    "reply_text": (row.get("reply_text") or "").strip(),
                    "sentiment":  (row.get("sentiment") or "none").strip(),
                }
    return replies


# ── Stage 2: Group engagements by person ──────────────────────────────────────

def group_by_person(engagements: list[dict], posts: dict[str, dict]) -> list[dict]:
    """Merge multiple engagements per person into one lead record."""
    grouped: dict[str, dict] = {}
    for eng in engagements:
        name = eng["name"]
        if name not in grouped:
            grouped[name] = {
                "name":         name,
                "title":        eng["title"],
                "company":      eng["company"],
                "company_size": eng["company_size"],
                "profile_url":  eng["profile_url"],
                "engagements":  [],
            }
        post = posts.get(eng["post_id"], {})
        grouped[name]["engagements"].append({
            "post_id":         eng["post_id"],
            "post_topic":      post.get("topic", ""),
            "post_text":       post.get("text", ""),
            "engagement_type": eng["engagement_type"],
            "comment_text":    eng["comment_text"],
            "engagement_date": eng["engagement_date"],
        })

    # Build a combined signal summary for each person
    for lead in grouped.values():
        engs = lead["engagements"]
        lead["post_ids"]       = list({e["post_id"] for e in engs})
        lead["comment_texts"]  = [e["comment_text"] for e in engs if e["comment_text"]]
        lead["engagement_types"] = [e["engagement_type"] for e in engs]
        # Best single engagement for display
        type_rank = {"comment": 3, "repost": 2, "like": 1}
        best = max(engs, key=lambda e: type_rank.get(e["engagement_type"], 0))
        lead["primary_post_id"]    = best["post_id"]
        lead["primary_post_topic"] = best["post_topic"]
        lead["primary_post_text"]  = best["post_text"]
        lead["primary_engagement"] = best["engagement_type"]
        lead["primary_comment"]    = best["comment_text"]

    return list(grouped.values())


# ── Stage 3: Intent scoring ────────────────────────────────────────────────────

def score_intent(lead: dict, today: date | None = None) -> float:
    """
    Compute a 0-10 intent score based on engagement type, recency, repeat
    engagement, and post topic intent.
    """
    today = today or date.today()
    engs  = lead["engagements"]

    # Post intent heuristic: AI-search topic = high, content POV = medium, other = low
    _post_intent: dict[str, float] = {}
    for e in engs:
        topic = e["post_topic"].lower()
        if "ai search" in topic or "aeo" in topic or "visibility" in topic:
            _post_intent[e["post_id"]] = 1.0
        elif "content" in topic or "pipeline" in topic:
            _post_intent[e["post_id"]] = 0.6
        else:
            _post_intent[e["post_id"]] = 0.3

    type_score = {"comment": 1.0, "repost": 0.6, "like": 0.3}

    # Score each engagement, take the max
    eng_scores = []
    for e in engs:
        try:
            eng_date = date.fromisoformat(e["engagement_date"])
        except (ValueError, TypeError):
            eng_date = today - timedelta(days=30)
        delta = (today - eng_date).days
        recency = 1.0 if delta <= 7 else (0.6 if delta <= 14 else 0.2)
        eng_s = type_score.get(e["engagement_type"], 0.3) * recency * _post_intent.get(e["post_id"], 0.5)
        eng_scores.append(eng_s)

    base = max(eng_scores) if eng_scores else 0.0

    # Repeat engagement bonus: +0.2 per extra post, cap +0.4
    extra_posts = len(lead["post_ids"]) - 1
    bonus = min(extra_posts * 0.2, 0.4)
    raw   = min(base + bonus, 1.0)

    return round(raw * 10, 1)   # 0–10


# ── Stage 3 continued: combined score + tier ──────────────────────────────────

def _tier(score: int, cfg: dict) -> str:
    if score >= cfg["hot_threshold"]:
        return "Hot"
    if score >= cfg["warm_low"]:
        return "Warm"
    return "Cool"


def score_and_qualify(leads: list[dict], cfg: dict) -> tuple[list[dict], list[dict]]:
    print(f"\n[3/8] Scoring {len(leads)} leads (ICP fit + intent)...")

    # ICP fit via shared scoring
    scored = score_fit_batch(leads, cfg["icp_text"], name_key="name")

    qualified = []
    disqualified = []

    fw = cfg["fit_weight"]
    iw = cfg["intent_weight"]

    for lead in scored:
        if lead.get("disqualified"):
            disqualified.append(lead)
            print(f"  DISQUALIFIED  {lead['name']:<24} {lead.get('disqualify_reason','')}")
            continue

        intent_score = score_intent(lead)
        lead["intent_score"] = intent_score

        fit_norm    = (lead["fit_score"] / 10) * 100
        intent_norm = (intent_score / 10) * 100
        composite   = round(fw * fit_norm + iw * intent_norm)
        lead["composite_score"] = composite
        lead["tier"] = _tier(composite, cfg)

        print(
            f"  {lead['name']:<26} fit={lead['fit_score']}/10  "
            f"intent={intent_score}/10  score={composite}  tier={lead['tier']}"
        )
        qualified.append(lead)

    qualified.sort(key=lambda l: l["composite_score"], reverse=True)
    return qualified, disqualified


# ── Stage 4: Draft sequences ───────────────────────────────────────────────────

def draft_sequences(qualified: list[dict], cfg: dict) -> list[dict]:
    print(f"\n[4/8] Drafting sequences ({len(qualified)} leads)...")

    sender_name    = cfg["sender_name"]
    sender_company = cfg["sender_company"]
    sender_offer   = cfg["sender_offer"]
    booking_link   = cfg["booking_link"]

    for lead in qualified:
        name          = lead["name"]
        title         = lead["title"]
        company       = lead["company"]
        company_size  = lead["company_size"]
        post_topic    = lead["primary_post_topic"]
        post_text     = lead["primary_post_text"]
        eng_type      = lead["primary_engagement"]
        comment_text  = lead["primary_comment"]
        post_id       = lead["primary_post_id"]
        fit_reason    = lead.get("fit_reason", "")

        context = (
            f"Lead: {name}, {title} at {company} ({company_size} people)\n"
            f"Sender: {sender_name} from {sender_company}\n"
            f"Offer: {sender_offer}\n"
            f"Booking link: {booking_link}\n"
            f"Post topic: {post_topic}\n"
            f"Post excerpt: {post_text[:300]}\n"
            f"Engagement type: {eng_type}\n"
            f"Comment/signal: {comment_text}\n"
            f"ICP fit reason: {fit_reason}\n"
        )

        print(f"  {name}...", end=" ", flush=True)

        conn_prompt = (
            "Write a LinkedIn connection note for someone who just engaged with a post.\n\n"
            f"{context}\n\n"
            "Rules:\n"
            "- Under 300 characters (hard limit).\n"
            "- Reference the specific post topic or comment text.\n"
            "- No generic opener. Just one direct sentence connecting their signal to why you are reaching out.\n"
            "- No em dashes. Plain, direct.\n"
            "Return only the connection note text."
        )
        connection_note = clean(query_text(conn_prompt))
        if len(connection_note) > 300:
            connection_note = connection_note[:297] + "..."

        msg1_prompt = (
            "Write LinkedIn message 1 (sent after connection is accepted).\n\n"
            f"{context}\n\n"
            "Rules:\n"
            "- Open with their specific comment or engagement signal, not a generic opener.\n"
            "- Connect their signal to the problem the sender solves.\n"
            "- Offer one concrete, low-friction next step.\n"
            "- 3-5 sentences. No filler, no em dashes, no hollow intensifiers.\n"
            "Return only the message text."
        )
        msg1 = clean(query_text(msg1_prompt))

        msg2_prompt = (
            "Write LinkedIn message 2 (sent only if no reply to message 1).\n\n"
            f"{context}\n\n"
            "Rules:\n"
            "- Add one new piece of specific detail not in message 1.\n"
            "- One clear CTA. 2-3 sentences. No filler, no em dashes.\n"
            "Return only the message text."
        )
        msg2 = clean(query_text(msg2_prompt))

        email_prompt = (
            "Write a cold email follow-up for a lead who has not replied on LinkedIn.\n\n"
            f"{context}\n\n"
            "Rules:\n"
            "- Subject line: plain and specific to their situation.\n"
            "- Body: 3-4 sentences. No filler openers. Reference the specific engagement.\n"
            "- End naturally with the booking link.\n"
            "- No em dashes. Direct, evidence-first.\n"
            "Return as:\nSubject: ...\n\n[body text]"
        )
        email_raw  = query_text(email_prompt)
        email_subj = ""
        email_body = ""
        subj_m = re.match(r"Subject:\s*(.+?)(?:\n|$)", email_raw, re.IGNORECASE)
        if subj_m:
            email_subj = subj_m.group(1).strip()
            email_body = clean(email_raw[subj_m.end():].strip())
        else:
            email_body = clean(email_raw)

        lead["sequence"] = {
            "connection_note": connection_note,
            "msg1":            msg1,
            "msg2":            msg2,
            "email_subject":   email_subj,
            "email_body":      email_body,
        }
        print("done")

    return qualified


# ── Stage 5-6: State machine + reply handling ──────────────────────────────────

def run_sequence_simulation(
    qualified: list[dict],
    replies: dict[str, dict],
    cfg: dict,
    output_dir: Path,
) -> None:
    print(f"\n[5/8] Simulating sequence states ({len(qualified)} leads)...")

    # Outbound engine skips warmup — these leads already engaged
    states = simulate_dry_run(
        qualified,
        replies,
        name_key="name",
        has_warmup_fn=lambda _: False,   # no warm-up comment touch
        sequence_def=cfg.get("sequence_def"),
        caps=cfg.get("caps"),
        base_date=date.today(),
    )

    state_map = {s.name: s for s in states}
    for lead in qualified:
        lead["_seq_state"] = state_map.get(lead["name"], SequenceState(name=lead["name"])).to_dict()

    # ICS for booked leads
    bookings_dir = output_dir / "bookings"
    bookings_dir.mkdir(parents=True, exist_ok=True)

    for lead in qualified:
        st = lead["_seq_state"]
        if st["state"] != "booked":
            continue
        name = lead["name"]
        print(f"  BOOKED: {name} at {lead['company']} — generating .ics")
        ics = make_ics(
            persona_name   = name,
            company        = lead["company"],
            sender_name    = cfg["sender_name"],
            sender_email   = f"{cfg['sender_name'].lower().replace(' ','.')}@example.com",
            attendee_email = f"{name.lower().replace(' ','.')}@example.com",
            booking_link   = cfg["booking_link"],
            summary_line   = f"Intro call: {cfg['sender_name']} + {name}",
            description    = f"Intro call. Offer: {cfg['sender_offer']}",
            meeting_date   = date.today() + timedelta(days=3),
        )
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        ics_path = bookings_dir / f"booking_{slug}.ics"
        ics_path.write_text(ics)
        lead["_ics_path"] = str(ics_path)

    for lead in qualified:
        st     = lead["_seq_state"]
        name   = lead["name"]
        state  = st["state"]
        label  = "BOOKED" if state == "booked" else ("stopped" if state == "stopped" else f"in sequence ({state})")
        print(f"  {lead['company']:<24} {name:<22} {label}")


# ── Stage 7: Attribution ───────────────────────────────────────────────────────

def build_attribution(qualified: list[dict], disqualified: list[dict], posts: dict) -> dict:
    """Which posts produced the most qualified leads and bookings."""
    attr: dict[str, dict] = {pid: {"post_id": pid, "topic": p.get("topic",""), "qualified": 0, "booked": 0}
                              for pid, p in posts.items()}
    for lead in qualified:
        for pid in lead.get("post_ids", []):
            if pid in attr:
                attr[pid]["qualified"] += 1
        if lead.get("_seq_state", {}).get("state") == "booked":
            primary = lead.get("primary_post_id", "")
            if primary in attr:
                attr[primary]["booked"] += 1
    return attr


# ── Output writers ─────────────────────────────────────────────────────────────

def write_sequences_md(
    qualified: list[dict],
    disqualified: list[dict],
    attribution: dict,
    output_dir: Path,
) -> Path:
    lines: list[str] = []
    lines += [
        "# Outbound engine: staged sequences (dry run)",
        "",
        "Leads who engaged with the posts, scored, qualified, and sequenced. "
        "Nothing has been sent. Every touch waits for human approval.",
        "",
    ]

    top_two = qualified[:2]
    rest    = qualified[2:]

    for i, lead in enumerate(top_two, 1):
        name    = lead["name"]
        title   = lead["title"]
        company = lead["company"]
        size    = lead["company_size"]
        score   = lead["composite_score"]
        tier    = lead["tier"]
        fit     = lead["fit_score"]
        intent  = lead.get("intent_score", 0)
        fit_r   = lead.get("fit_reason", "")
        comment = lead["primary_comment"]
        topic   = lead["primary_post_topic"]
        seq     = lead.get("sequence", {})
        st      = lead.get("_seq_state", {})
        state   = st.get("state", "")
        rtext   = st.get("reply_text", "")
        ics     = lead.get("_ics_path", "")

        lines.append("---")
        lines.append("")
        lines.append(f"## {i}. {name}, {title}, {company} ({size} people). Tier: {tier}. Score: {score}")
        lines.append("")
        lines.append(f"- Fit {fit}/10: {fit_r}")
        lines.append(f"- Intent {intent}/10: {'commented' if lead['primary_engagement'] == 'comment' else lead['primary_engagement']} on the {topic} post" + (f" (\"{comment}\")" if comment else "") + ".")
        lines.append(f"- Source: {lead.get('primary_post_id','')}")
        lines.append("")

        lines.append(f"**Connection note** (LinkedIn, {len(seq.get('connection_note',''))} chars)")
        lines.append(seq.get("connection_note", ""))
        lines.append("")

        lines.append("**Message 1** (day 1, after connection accepted)")
        lines.append(seq.get("msg1", ""))
        lines.append("")

        lines.append("**Message 2** (day 4, only if no reply)")
        lines.append(seq.get("msg2", ""))
        lines.append("")

        lines.append("**Email follow-up** (day 8, optional channel)")
        if seq.get("email_subject"):
            lines.append(f"Subject: {seq['email_subject']}")
        lines.append(seq.get("email_body", ""))
        lines.append("")

        if state == "booked":
            outcome = "replied positive"
            if rtext:
                outcome += f" (\"{rtext}\")"
            outcome += ". Sequence stopped. Meeting booked."
            if ics:
                outcome += f" See bookings/{Path(ics).name}."
        elif state == "stopped":
            outcome = f"replied with a deferral (\"{rtext}\"). Sequence stopped politely." if rtext else "negative reply. Sequence stopped."
        else:
            outcome = f"no reply yet. Advanced to {state} on schedule."
        lines.append(f"**Dry-run outcome:** {outcome}")
        lines.append("")

    if rest or disqualified:
        lines += ["---", "", "## Note on the rest of the queue"]
        for lead in rest:
            st    = lead.get("_seq_state", {})
            state = st.get("state", "")
            if state == "booked":
                note = "Meeting booked."
            elif state == "stopped":
                note = "Sequence stopped politely."
            else:
                note = f"In sequence ({state})."
            lines.append(
                f"- {lead['name']} ({lead['title']}, {lead['company']}): {lead['tier']}. "
                f"Source: {lead.get('primary_post_id','')} ({lead.get('primary_post_topic','')[:40]}). {note}"
            )
        for lead in disqualified:
            lines.append(f"- Disqualified: {lead['name']} ({lead.get('disqualify_reason','outside ICP')})")

    if attribution:
        lines += ["", "---", "", "## Post attribution"]
        for pid, data in sorted(attribution.items()):
            lines.append(
                f"- {pid} ({data['topic'][:50]}): "
                f"{data['qualified']} qualified lead(s), {data['booked']} booking(s)"
            )

    out = output_dir / "sequences.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def write_approval_queue(
    qualified: list[dict],
    disqualified: list[dict],
    attribution: dict,
    posts: dict,
    total_engagements: int,
    output_dir: Path,
) -> Path:
    total_people = len(qualified) + len(disqualified)
    n_qual    = len(qualified)
    n_disq    = len(disqualified)
    n_booked  = sum(1 for l in qualified if l.get("_seq_state", {}).get("state") == "booked")
    n_stopped = sum(1 for l in qualified if l.get("_seq_state", {}).get("state") == "stopped")
    n_seq     = n_qual - n_booked - n_stopped

    def _tier_class(tier: str) -> str:
        return {"Hot": "hot", "Warm": "warm", "Cool": "cool"}.get(tier, "cool")

    def _status_html(lead: dict) -> str:
        st = lead.get("_seq_state", {}).get("state", "")
        if st == "booked":
            return '<span class="status booked">Booked</span>'
        if st == "stopped":
            return '<span class="status stopped">Stopped</span>'
        touch_labels = {"connection_sent": "connection sent", "connected": "connected",
                        "msg1": "msg 1", "msg2": "msg 2", "email": "email"}
        return f'<span class="status">In sequence ({touch_labels.get(st, st)})</span>'

    rows_html = ""
    for i, lead in enumerate(qualified, 1):
        name    = lead["name"]
        title   = lead["title"]
        company = lead["company"]
        size    = lead["company_size"]
        fit     = lead["fit_score"]
        intent  = lead.get("intent_score", 0)
        tier    = lead["tier"]
        score   = lead["composite_score"]
        source  = f"{lead.get('primary_post_id','')} {lead.get('primary_post_topic','')[:25]}"
        seq     = lead.get("sequence", {})
        conn    = seq.get("connection_note", "")
        preview = conn[:140].replace('"', "&quot;")

        rows_html += f"""      <tr>
        <td>{i}</td>
        <td>{name}<br><span class="status">{title}</span></td>
        <td>{company} ({size})</td>
        <td>{fit}</td><td>{intent}</td>
        <td class="tier {_tier_class(tier)}">{tier} {score}</td>
        <td>{source}</td>
        <td>{_status_html(lead)}</td>
        <td class="preview">"{preview}..."</td>
      </tr>
"""

    dq_html = ""
    for lead in disqualified:
        dq_html += (
            f'<p class="dq"><b>{lead["name"]}</b> ({lead.get("title","")}, {lead.get("company","")})'
            f' — {lead.get("disqualify_reason","outside ICP")}</p>\n'
        )

    # Attribution bar chart (simple text bars)
    attr_rows = ""
    max_q = max((d["qualified"] for d in attribution.values()), default=1) or 1
    for pid, data in sorted(attribution.items()):
        pct = int((data["qualified"] / max_q) * 100)
        attr_rows += (
            f'<tr><td style="white-space:nowrap">{pid}</td>'
            f'<td style="color:#475467;font-size:13px">{data["topic"][:55]}</td>'
            f'<td><div class="bar"><i style="width:{pct}%"></i></div></td>'
            f'<td style="text-align:right;font-size:13px">{data["qualified"]} qualified</td>'
            f'<td style="text-align:right;font-size:13px">{data["booked"]} booked</td></tr>\n'
        )

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Outbound engine: approval queue (dry run)</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1a1a1a; background: #f6f7f9; margin: 0; padding: 32px; }}
  .wrap {{ max-width: 980px; margin: 0 auto; }}
  h1 {{ font-size: 22px; margin: 0 0 4px; }}
  .sub {{ color: #666; margin: 0 0 24px; }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 28px; }}
  .chip {{ background: #fff; border: 1px solid #e3e6ea; border-radius: 8px; padding: 10px 14px; }}
  .chip b {{ display: block; font-size: 20px; }}
  .chip span {{ color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: .04em; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e3e6ea; border-radius: 10px; overflow: hidden; margin: 0 0 28px; }}
  th, td {{ text-align: left; padding: 11px 12px; border-bottom: 1px solid #eef0f2; vertical-align: top; }}
  th {{ background: #fafbfc; font-size: 12px; text-transform: uppercase; letter-spacing: .03em; color: #555; }}
  tr:last-child td {{ border-bottom: 0; }}
  .tier {{ font-weight: 600; }}
  .hot {{ color: #b42318; }}
  .warm {{ color: #b54708; }}
  .cool {{ color: #475467; }}
  .status {{ font-size: 13px; }}
  .booked {{ color: #067647; font-weight: 600; }}
  .stopped {{ color: #98a2b3; }}
  .preview {{ color: #475467; font-size: 13px; max-width: 320px; }}
  h2 {{ font-size: 16px; margin: 28px 0 10px; }}
  .panel {{ background: #fff; border: 1px solid #e3e6ea; border-radius: 10px; padding: 16px 18px; margin: 0 0 18px; }}
  .dq {{ color: #667085; font-size: 14px; }}
  .bar {{ height: 8px; background: #eef0f2; border-radius: 4px; overflow: hidden; }}
  .bar i {{ display: block; height: 100%; background: #067647; }}
  .foot {{ color: #98a2b3; font-size: 12px; margin-top: 24px; line-height: 1.6; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Outbound engine: approval queue</h1>
  <p class="sub">Dry run. Source: engagement on {len(posts)} posts. {total_engagements} engagements, {total_people} people, {n_qual} qualified. Nothing has been sent.</p>

  <div class="chips">
    <div class="chip"><b>{total_people}</b><span>Leads scored</span></div>
    <div class="chip"><b>{n_qual}</b><span>Qualified</span></div>
    <div class="chip"><b>{n_disq}</b><span>Disqualified</span></div>
    <div class="chip"><b>{n_booked}</b><span>Booked</span></div>
    <div class="chip"><b>{n_seq}</b><span>In sequence</span></div>
    <div class="chip"><b>{n_stopped}</b><span>Stopped</span></div>
  </div>

  <table>
    <thead>
      <tr><th>#</th><th>Lead</th><th>Company</th><th>Fit</th><th>Intent</th><th>Tier</th><th>Source</th><th>Status</th><th>First touch (awaiting approval)</th></tr>
    </thead>
    <tbody>
{rows_html}    </tbody>
  </table>

  <h2>Disqualified</h2>
  <div class="panel">
{dq_html}  </div>

  <h2>Post attribution</h2>
  <div class="panel">
    <table style="border:0;background:transparent">
      <tbody>
        {attr_rows}
      </tbody>
    </table>
  </div>

  <p class="foot">
    <b>Note.</b> LinkedIn's User Agreement prohibits unauthorized automation. This engine is human-in-the-loop by default.
    Every touch above is staged and awaiting approval. Nothing has been sent.
    The live send route (--live) uses a single sanctioned API (Unipile) with safe daily caps enforced in code.
  </p>
</div>
</body>
</html>
"""
    out = output_dir / "approval_queue.html"
    out.write_text(html, encoding="utf-8")
    return out


def write_state_json(
    qualified: list[dict],
    disqualified: list[dict],
    output_dir: Path,
) -> Path:
    state = {
        "qualified": [
            {
                "name":        l["name"],
                "title":       l["title"],
                "company":     l["company"],
                "score":       l["composite_score"],
                "tier":        l["tier"],
                "fit_score":   l["fit_score"],
                "intent_score": l.get("intent_score"),
                "seq_state":   l.get("_seq_state"),
                "ics_path":    l.get("_ics_path", ""),
            }
            for l in qualified
        ],
        "disqualified": [
            {"name": l["name"], "reason": l.get("disqualify_reason", "")}
            for l in disqualified
        ],
    }
    out = output_dir / "state.json"
    out.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return out


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run(args) -> None:
    if os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ERROR: ANTHROPIC_API_KEY is set. This repo runs on a Claude subscription, "
            "not an API key. Unset it first:\n  unset ANTHROPIC_API_KEY"
        )
        sys.exit(1)

    dry_run = not args.live

    print("=" * 60)
    print("OUTBOUND ENGINE — signal-to-meeting engine")
    print(f"Mode:        {'dry-run (no sends)' if dry_run else 'LIVE (staged, approval required)'}")
    print(f"Config:      {args.config}")
    print(f"Posts:       {args.posts}")
    print(f"Engagements: {args.engagements}")
    print("=" * 60)

    # Stage 1: Ingest
    print("\n[1/8] Ingesting data...")
    cfg         = load_config(args.config)
    posts       = load_posts(args.posts)
    engagements = load_engagements(args.engagements)
    replies     = load_replies(getattr(args, "replies", None) or "")
    print(f"  {len(posts)} posts  |  {len(engagements)} engagements  |  {len(replies)} reply fixtures")

    # Stage 2: Group by person
    print(f"\n[2/8] Grouping {len(engagements)} engagements by person...")
    leads = group_by_person(engagements, posts)
    print(f"  {len(leads)} unique people found")
    for l in leads:
        engs_summary = ", ".join(set(l["engagement_types"]))
        print(f"  {l['name']:<26} {l['title']:<30} {l['company']} — {engs_summary}")

    # Stage 3: Score + qualify
    qualified, disqualified = score_and_qualify(leads, cfg)
    print(f"\n  Summary: {len(qualified)} qualified  |  {len(disqualified)} disqualified")

    # Stage 4: Draft sequences
    qualified = draft_sequences(qualified, cfg)

    # Set up output dir
    out_slug   = re.sub(r"[^a-z0-9]+", "_", cfg.get("sender_company", "outbound").lower()).strip("_")
    output_dir = _REPO_ROOT / "outputs" / f"outbound_{out_slug}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Stage 5-6: State machine + booking
    run_sequence_simulation(qualified, replies, cfg, output_dir)

    # Stage 7: Attribution
    print("\n[7/8] Building attribution...")
    attribution = build_attribution(qualified, disqualified, posts)
    for pid, data in sorted(attribution.items()):
        print(f"  {pid}: {data['topic'][:40]:<42} {data['qualified']} qualified  {data['booked']} booked")

    # Stage 8: Write outputs
    print(f"\n[8/8] Writing outputs to {output_dir}/")
    seq_path   = write_sequences_md(qualified, disqualified, attribution, output_dir)
    queue_path = write_approval_queue(qualified, disqualified, attribution, posts, len(engagements), output_dir)
    state_path = write_state_json(qualified, disqualified, output_dir)

    print(f"\n  sequences.md      → {seq_path}")
    print(f"  approval_queue.html → {queue_path}")
    print(f"  state.json        → {state_path}")
    ics_files = list((output_dir / "bookings").glob("*.ics")) if (output_dir / "bookings").exists() else []
    for f in ics_files:
        print(f"  bookings/{f.name}")

    n_booked  = sum(1 for l in qualified if l.get("_seq_state", {}).get("state") == "booked")
    n_stopped = sum(1 for l in qualified if l.get("_seq_state", {}).get("state") == "stopped")
    n_seq     = len(qualified) - n_booked - n_stopped
    print("\n" + "=" * 60)
    print(f"Done.  {len(qualified)} qualified  |  {n_booked} booked  |  {n_seq} in sequence  |  {n_stopped} stopped  |  {len(disqualified)} disqualified")
    print("=" * 60)
    if dry_run:
        print("\nAll actions are staged for approval. Nothing was sent.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Outbound Engine — signal-to-meeting engine"
    )
    sub   = parser.add_subparsers(dest="command")
    run_p = sub.add_parser("run", help="Run the outbound pipeline")
    run_p.add_argument("--config",      required=True, help="Path to outbound_config.md")
    run_p.add_argument("--posts",       required=True, help="Path to posts.csv")
    run_p.add_argument("--engagements", required=True, help="Path to engagements.csv")
    run_p.add_argument("--replies",     default=None,  help="Path to replies_fixture.csv (dry-run)")
    run_p.add_argument("--dry-run",     action="store_true", default=True)
    run_p.add_argument("--live",        action="store_true", default=False)
    args = parser.parse_args()
    if args.command == "run":
        run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
