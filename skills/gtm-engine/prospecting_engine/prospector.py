"""
Prospecting Engine — trigger-based outbound prospecting.

Turns a list of target accounts into a researched, personalized, compliant
engagement plan. Runs fully offline in dry-run on the included sample data.

Usage
-----
python prospecting_engine/prospector.py run \\
    --config prospecting_engine/samples/prospector_config.md \\
    --accounts prospecting_engine/samples/target_accounts.csv \\
    --replies prospecting_engine/samples/replies_fixture.csv \\
    --dry-run

Add --live to stage real actions via Unipile (requires UNIPILE_API_KEY).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

# Ensure repo root is on the path when the script is run from any directory.
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from shared.antislop import clean
from shared.llm import query_json, query_text
from shared.report import Section, render
from shared.scoring import score_fit_batch
from shared.sequence import SequenceState, make_ics, simulate_dry_run
from shared.ai_visibility import check_visibility


# ── Config parsing ─────────────────────────────────────────────────────────────

def load_config(path: str) -> dict:
    text = Path(path).read_text()
    cfg: dict = {"raw": text}

    def _extract(label: str, default: str = "") -> str:
        m = re.search(rf"{re.escape(label)}\s*[:\-]\s*(.+)", text, re.IGNORECASE)
        return m.group(1).strip() if m else default

    cfg["sender_name"]     = _extract("Name")
    cfg["sender_company"]  = _extract("Company")
    cfg["sender_offer"]    = _extract("Offer")
    cfg["booking_link"]    = _extract("Booking link")
    cfg["fit_weight"]      = float(_extract("Fit weight", "0.4"))
    cfg["trigger_weight"]  = float(_extract("Trigger strength weight", "0.3"))
    cfg["wedge_weight"]    = float(_extract("Wedge clarity weight", "0.3"))

    # Tiers
    hot_m  = re.search(r"Hot\s*[>=]+\s*(\d+)", text, re.IGNORECASE)
    warm_m = re.search(r"Warm\s+(\d+)\s+to\s+(\d+)", text, re.IGNORECASE)
    cfg["hot_threshold"]  = int(hot_m.group(1))  if hot_m  else 80
    cfg["warm_low"]       = int(warm_m.group(1)) if warm_m else 60
    cfg["warm_high"]      = int(warm_m.group(2)) if warm_m else 79

    # Daily caps
    cap_c = re.search(r"Comments per day\s*[:\-]\s*(\d+)", text, re.IGNORECASE)
    cap_x = re.search(r"Connection requests per day\s*[:\-]\s*(\d+)", text, re.IGNORECASE)
    cap_m = re.search(r"Messages per day\s*[:\-]\s*(\d+)", text, re.IGNORECASE)
    cfg["caps"] = {
        "comments":    int(cap_c.group(1)) if cap_c else 15,
        "connections": int(cap_x.group(1)) if cap_x else 20,
        "messages":    int(cap_m.group(1)) if cap_m else 30,
    }

    # Sequence day offsets
    seq_labels = {
        "warmup":           r"Day\s*0",
        "connection_sent":  r"Day\s*2",
        "msg1":             r"Day\s*3",
        "msg2":             r"Day\s*6",
        "email":            r"Day\s*10",
    }
    cfg["sequence_def"] = {}
    for touch, pattern in seq_labels.items():
        m = re.search(pattern, text, re.IGNORECASE)
        default_days = {"warmup": 0, "connection_sent": 2, "msg1": 3, "msg2": 6, "email": 10}
        cfg["sequence_def"][touch] = default_days[touch]

    # ICP text — everything under "## ICP" until the next ## section
    icp_m = re.search(r"##\s*ICP\s*\n(.*?)(?=\n##|\Z)", text, re.DOTALL | re.IGNORECASE)
    cfg["icp_text"] = icp_m.group(1).strip() if icp_m else text

    return cfg


# ── CSV loaders ────────────────────────────────────────────────────────────────

def load_accounts(path: str) -> list[dict]:
    accounts = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append({k: (v or "").strip() for k, v in row.items()})
    return accounts


def load_replies(path: str) -> dict[str, dict]:
    replies: dict[str, dict] = {}
    if not path or not Path(path).exists():
        return replies
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or "").strip()
            if name:
                replies[name] = {
                    "touch":      (row.get("touch") or "").strip(),
                    "reply_text": (row.get("reply_text") or "").strip(),
                    "sentiment":  (row.get("sentiment") or "none").strip(),
                }
    return replies


# ── Stage helpers ──────────────────────────────────────────────────────────────

def _tier(score: int, cfg: dict) -> str:
    if score >= cfg["hot_threshold"]:
        return "Hot"
    if score >= cfg["warm_low"]:
        return "Warm"
    return "Cool"


def detect_triggers(accounts: list[dict], dry_run: bool) -> list[dict]:
    """Stage 2: classify trigger type and strength for each account."""
    print(f"\n[2/8] Detecting triggers for {len(accounts)} accounts...")
    priority_map = {
        "ai_visibility":  10,
        "funding":        8,
        "new exec":       7,
        "new_exec":       7,
        "hiring":         6,
        "launch":         5,
        "content":        4,
        "none":           0,
    }
    for acc in accounts:
        raw_type = (acc.get("trigger_type") or "none").lower().strip()
        acc["trigger_strength"] = priority_map.get(raw_type, 3)
        if not dry_run:
            # In live mode: check the public signal URL if available
            pass
        print(f"  {acc.get('company',''):<28} trigger={raw_type}  strength={acc['trigger_strength']}")
    return accounts


def generate_wedges(accounts: list[dict], dry_run: bool) -> list[dict]:
    """Stage 3: generate AI-visibility wedge for each account."""
    print(f"\n[3/8] Generating AI-visibility wedges...")
    for acc in accounts:
        vis = check_visibility(acc, dry_run=dry_run)
        acc["ai_vis_has_gap"]  = vis["has_gap"]
        acc["ai_vis_summary"]  = vis["gap_summary"]
        acc["ai_vis_strength"] = vis["strength"]

        if vis["has_gap"]:
            acc["wedge"] = vis["gap_summary"]
            acc["wedge_clarity"] = vis["strength"]
            acc["lead_hook"] = "ai_visibility"
        else:
            # Fall back to the strongest trigger as the hook
            trigger_text = acc.get("public_signal", "").strip()
            acc["wedge"] = trigger_text[:120] if trigger_text else ""
            acc["wedge_clarity"] = acc.get("trigger_strength", 3)
            acc["lead_hook"] = acc.get("trigger_type", "none")

        print(f"  {acc.get('company',''):<28} wedge={acc['lead_hook']}  clarity={acc['wedge_clarity']}")
    return accounts


def score_and_qualify(accounts: list[dict], cfg: dict) -> tuple[list[dict], list[dict]]:
    """Stage 4+5: ICP fit scoring + composite score + disqualification."""
    print(f"\n[4/8] Scoring ICP fit ({len(accounts)} accounts)...")
    scored = score_fit_batch(accounts, cfg["icp_text"], name_key="company")

    fw = cfg["fit_weight"]
    tw = cfg["trigger_weight"]
    ww = cfg["wedge_weight"]

    qualified = []
    disqualified = []

    for acc in scored:
        if acc.get("disqualified"):
            disqualified.append(acc)
            print(f"  DISQUALIFIED  {acc.get('company',''):<28} {acc.get('disqualify_reason','')}")
            continue

        fit_norm     = (acc["fit_score"] / 10) * 100
        trigger_norm = (acc.get("trigger_strength", 0) / 10) * 100
        wedge_norm   = (acc.get("wedge_clarity", 0) / 10) * 100

        composite = round(fw * fit_norm + tw * trigger_norm + ww * wedge_norm)
        acc["composite_score"] = composite
        acc["tier"] = _tier(composite, cfg)

        print(
            f"  {acc.get('company',''):<28} "
            f"fit={acc['fit_score']}/10  "
            f"trigger={acc.get('trigger_strength',0)}/10  "
            f"wedge={acc.get('wedge_clarity',0)}/10  "
            f"score={composite}  tier={acc['tier']}"
        )
        qualified.append(acc)

    qualified.sort(key=lambda a: a["composite_score"], reverse=True)
    return qualified, disqualified


def draft_engagement_plans(qualified: list[dict], cfg: dict) -> list[dict]:
    """Stage 6: draft compliant engagement plan per account through antislop."""
    print(f"\n[6/8] Drafting engagement plans ({len(qualified)} accounts)...")

    sender_name    = cfg["sender_name"]
    sender_company = cfg["sender_company"]
    sender_offer   = cfg["sender_offer"]
    booking_link   = cfg["booking_link"]

    for acc in qualified:
        company        = acc.get("company", "")
        persona_name   = acc.get("target_persona_name", "")
        persona_title  = acc.get("target_persona_title", "")
        trigger_type   = acc.get("trigger_type", "")
        public_signal  = acc.get("public_signal", "")
        ai_sig         = acc.get("ai_visibility_signal", "")
        recent_post    = acc.get("recent_post_excerpt", "").strip()
        wedge          = acc.get("wedge", "")
        lead_hook      = acc.get("lead_hook", "")
        fit_score      = acc.get("fit_score", 5)
        fit_reason     = acc.get("fit_reason", "")

        has_warmup     = bool(recent_post)

        # Build prompt with all context
        context = (
            f"Company: {company}\n"
            f"Persona: {persona_name}, {persona_title}\n"
            f"Trigger: {trigger_type} — {public_signal}\n"
            f"AI visibility gap: {ai_sig}\n"
            f"Recent post excerpt: {recent_post}\n"
            f"Wedge/lead hook: {wedge} (hook type: {lead_hook})\n"
            f"ICP fit: {fit_score}/10 — {fit_reason}\n"
            f"Sender: {sender_name} from {sender_company}\n"
            f"Offer: {sender_offer}\n"
            f"Booking link: {booking_link}\n"
        )

        print(f"  {company} ({persona_name})...", end=" ", flush=True)

        warmup_comment = ""
        if has_warmup:
            warmup_prompt = (
                "Write a warm-up comment for this cold prospect's recent LinkedIn post.\n\n"
                f"{context}\n"
                f"The post says: \"{recent_post}\"\n\n"
                "Rules:\n"
                "- Genuine observation that adds value. No pitch. No mention of the sender's company or offer.\n"
                "- Connects naturally to the AI-search angle if the post topic allows it.\n"
                "- 2-3 sentences max. No filler openers (Absolutely, Great post, etc.).\n"
                "- Plain declarative sentences. No em dashes.\n"
                "Return just the comment text, nothing else."
            )
            warmup_comment = clean(query_text(warmup_prompt))

        connection_prompt = (
            "Write a LinkedIn connection note for a cold prospect.\n\n"
            f"{context}\n\n"
            "Rules:\n"
            "- Under 300 characters (hard limit).\n"
            "- One sentence referencing the specific trigger or AI-visibility gap.\n"
            "- No generic openers. No pitch. Just the reason and a short hook.\n"
            "- No em dashes. Plain, direct.\n"
            "Return just the connection note text."
        )
        connection_note = clean(query_text(connection_prompt))
        # Hard-trim to 300 chars
        if len(connection_note) > 300:
            connection_note = connection_note[:297] + "..."

        msg1_prompt = (
            "Write LinkedIn message 1 for a cold prospect after connecting.\n\n"
            f"{context}\n\n"
            "Rules:\n"
            "- Lead with the AI-visibility wedge if one exists; otherwise lead with the strongest trigger.\n"
            "- Reference the specific trigger evidence (funding date, podcast, job post, launch).\n"
            "- Describe what the gap means for them in one sentence.\n"
            "- Offer one concrete next step: run the gap analysis, or show the specific queries.\n"
            "- 3-5 sentences. No filler, no em dashes, no hollow intensifiers.\n"
            "Return just the message text."
        )
        msg1 = clean(query_text(msg1_prompt))

        msg2_prompt = (
            "Write LinkedIn message 2 for a cold prospect (sent only if no reply to message 1).\n\n"
            f"{context}\n\n"
            "Rules:\n"
            "- Acknowledge they may be busy.\n"
            "- Add one new specific detail they have not heard yet (a query name, a competitor, a count).\n"
            "- One clear CTA. 2-3 sentences. No filler, no em dashes.\n"
            "Return just the message text."
        )
        msg2 = clean(query_text(msg2_prompt))

        email_prompt = (
            "Write a cold email follow-up for a prospect who has not replied on LinkedIn.\n\n"
            f"{context}\n\n"
            "Rules:\n"
            "- Subject line: one plain sentence, specific to their situation.\n"
            "- Body: 3-4 sentences. No filler openers. Reference the trigger and the gap.\n"
            "- End with the booking link naturally.\n"
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

        acc["plan"] = {
            "warmup_comment":  warmup_comment,
            "connection_note": connection_note,
            "msg1":            msg1,
            "msg2":            msg2,
            "email_subject":   email_subj,
            "email_body":      email_body,
            "has_warmup":      has_warmup,
        }
        print("done")

    return qualified


def run_sequence_simulation(
    qualified: list[dict],
    replies: dict[str, dict],
    cfg: dict,
    output_dir: Path,
    dry_run: bool,
) -> list[SequenceState]:
    """Stage 7: state machine + reply handling + ICS generation."""
    print(f"\n[7/8] Simulating sequence states ({len(qualified)} accounts)...")

    def has_warmup_fn(acc: dict) -> bool:
        return bool(acc.get("recent_post_excerpt", "").strip())

    states = simulate_dry_run(
        qualified,
        replies,
        name_key="target_persona_name",
        has_warmup_fn=has_warmup_fn,
        sequence_def=cfg.get("sequence_def"),
        caps=cfg.get("caps"),
        base_date=date.today(),
    )

    # Attach state back onto account for reporting
    state_map = {s.name: s for s in states}
    for acc in qualified:
        pname = acc.get("target_persona_name", "")
        acc["_seq_state"] = state_map.get(pname, SequenceState(name=pname)).to_dict()

    # Generate .ics for booked states
    bookings_dir = output_dir / "bookings"
    bookings_dir.mkdir(parents=True, exist_ok=True)

    for acc in qualified:
        st = acc["_seq_state"]
        if st["state"] != "booked":
            continue
        pname = acc.get("target_persona_name", "")
        print(f"  BOOKED: {pname} at {acc.get('company','')} — generating .ics")
        ics_content = make_ics(
            persona_name   = pname,
            company        = acc.get("company", ""),
            sender_name    = cfg["sender_name"],
            sender_email   = f"{cfg['sender_name'].lower().replace(' ','.')}@example.com",
            attendee_email = f"{pname.lower().replace(' ','.')}@example.com",
            booking_link   = cfg["booking_link"],
            summary_line   = f"Intro call: {cfg['sender_name']} + {pname}",
            description    = f"Intro call booked via prospecting engine. Offer: {cfg['sender_offer']}",
            meeting_date   = date.today() + timedelta(days=3),
        )
        slug = re.sub(r"[^a-z0-9]+", "_", pname.lower()).strip("_")
        ics_path = bookings_dir / f"booking_{slug}.ics"
        ics_path.write_text(ics_content)
        acc["_ics_path"] = str(ics_path)

    for acc in qualified:
        st   = acc["_seq_state"]
        pname = acc.get("target_persona_name", "")
        company = acc.get("company", "")
        status  = st["state"]
        if status == "booked":
            label = "BOOKED"
        elif status == "stopped":
            label = "stopped (politely)"
        else:
            label = f"in sequence ({status})"
        print(f"  {company:<28} {pname:<24} {label}")

    return states


# ── Output writers ─────────────────────────────────────────────────────────────

def write_prospecting_plan(
    qualified: list[dict],
    disqualified: list[dict],
    output_dir: Path,
) -> Path:
    """Write prospecting_plan.md matching the example output format."""
    lines: list[str] = []
    lines.append("# Prospecting engine: staged engagement plans (dry run)")
    lines.append("")
    lines.append(
        "Top-ranked cold accounts with research, trigger, AI-visibility wedge, score, "
        "and full staged engagement plan. Nothing has been sent. Every action waits for "
        "human approval."
    )
    lines.append("")

    top_two = qualified[:2]
    rest    = qualified[2:]

    for i, acc in enumerate(top_two, 1):
        company      = acc.get("company", "")
        pname        = acc.get("target_persona_name", "")
        ptitle       = acc.get("target_persona_title", "")
        score        = acc.get("composite_score", 0)
        tier         = acc.get("tier", "")
        fit_score    = acc.get("fit_score", 0)
        fit_reason   = acc.get("fit_reason", "")
        trigger_type = acc.get("trigger_type", "")
        trigger_str  = acc.get("trigger_strength", 0)
        wedge_str    = acc.get("wedge_clarity", 0)
        public_sig   = acc.get("public_signal", "")
        ai_sig       = acc.get("ai_visibility_signal", "")
        wedge        = acc.get("wedge", "")
        plan         = acc.get("plan", {})
        seq_state    = acc.get("_seq_state", {})

        lines.append(f"---")
        lines.append("")
        lines.append(f"## {i}. {company}. Persona: {pname}, {ptitle}. Tier: {tier}. Score: {score}")
        lines.append("")
        lines.append("Research summary")
        lines.append(f"- Trigger: {public_sig}")
        if ai_sig:
            lines.append(f"- Wedge (AI visibility): {ai_sig}")
        lines.append(f"- Fit {fit_score}/10: {fit_reason}")
        lines.append(
            f"- Score: fit {fit_score}, trigger strength {trigger_str} ({trigger_type}), "
            f"wedge clarity {wedge_str}."
        )
        lines.append("")

        if plan.get("warmup_comment"):
            lines.append(f"**Warm-up comment** on their recent post:")
            lines.append(plan["warmup_comment"])
            lines.append("")

        lines.append(f"**Connection note** (LinkedIn, {len(plan.get('connection_note',''))} chars):")
        lines.append(plan.get("connection_note", ""))
        lines.append("")

        lines.append("**Message 1** (lead with the wedge):")
        lines.append(plan.get("msg1", ""))
        lines.append("")

        lines.append("**Message 2** (only if no reply):")
        lines.append(plan.get("msg2", ""))
        lines.append("")

        lines.append("**Email follow-up** (optional channel):")
        if plan.get("email_subject"):
            lines.append(f"Subject: {plan['email_subject']}")
        lines.append(plan.get("email_body", ""))
        lines.append("")

        state_name = seq_state.get("state", "")
        reply_text = seq_state.get("reply_text", "")
        ics_path   = acc.get("_ics_path", "")
        if state_name == "booked":
            outcome = f"replied positive"
            if reply_text:
                outcome += f" (\"{reply_text}\")"
            outcome += ". Sequence stopped. Meeting booked."
            if ics_path:
                slug = Path(ics_path).name
                outcome += f" See bookings/{slug}."
            lines.append(f"Dry-run outcome: {outcome}")
        elif state_name == "stopped":
            lines.append(
                f"Dry-run outcome: replied with a deferral. Sequence stopped politely. "
                f"Reply text: \"{reply_text}\"." if reply_text
                else "Dry-run outcome: no reply. Sequence advanced to next touch."
            )
        else:
            lines.append(
                f"Dry-run outcome: connection accepted, no reply yet, advanced to {state_name} on schedule."
            )
        lines.append("")

    if rest or disqualified:
        lines.append("---")
        lines.append("")
        lines.append("## Note on the rest of the queue")
        for acc in rest:
            company    = acc.get("company", "")
            pname      = acc.get("target_persona_name", "")
            ptitle     = acc.get("target_persona_title", "")
            tier       = acc.get("tier", "")
            trigger    = acc.get("trigger_type", "")
            wedge      = acc.get("wedge", "")
            seq_state  = acc.get("_seq_state", {})
            state_name = seq_state.get("state", "")
            if state_name == "booked":
                status_note = "Meeting booked."
            elif state_name == "stopped":
                status_note = "Sequence stopped politely."
            else:
                status_note = f"In sequence ({state_name})."
            lines.append(
                f"- {company} ({pname}, {ptitle}): {tier}. "
                f"Trigger: {trigger}. Wedge: {wedge[:80] if wedge else 'none'}. {status_note}"
            )
        for acc in disqualified:
            company = acc.get("company", "")
            reason  = acc.get("disqualify_reason", "outside ICP")
            lines.append(f"- Disqualified: {company} ({reason})")

    out_path = output_dir / "prospecting_plan.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def write_prospecting_queue(
    qualified: list[dict],
    disqualified: list[dict],
    output_dir: Path,
) -> Path:
    """Write prospecting_queue.html matching the example output format."""
    total     = len(qualified) + len(disqualified)
    n_qual    = len(qualified)
    n_disq    = len(disqualified)
    n_booked  = sum(1 for a in qualified if a.get("_seq_state", {}).get("state") == "booked")
    n_stopped = sum(1 for a in qualified if a.get("_seq_state", {}).get("state") == "stopped")
    n_seq     = n_qual - n_booked - n_stopped

    def _tier_class(tier: str) -> str:
        return {"Hot": "hot", "Warm": "warm", "Cool": "cool"}.get(tier, "cool")

    def _status_label(acc: dict) -> str:
        st = acc.get("_seq_state", {}).get("state", "")
        if st == "booked":
            return '<span class="status booked">Booked</span>'
        if st == "stopped":
            return '<span class="status stopped">Stopped</span>'
        touch_labels = {
            "warmup":          "warm-up comment",
            "connection_sent": "connection sent",
            "connected":       "connected",
            "msg1":            "message 1",
            "msg2":            "message 2",
            "email":           "email",
        }
        label = touch_labels.get(st, st)
        return f'<span class="status">In sequence ({label})</span>'

    rows_html = ""
    for i, acc in enumerate(qualified, 1):
        company    = acc.get("company", "")
        pname      = acc.get("target_persona_name", "")
        ptitle     = acc.get("target_persona_title", "")
        fit        = acc.get("fit_score", 0)
        trigger    = acc.get("trigger_type", "").replace("_", " ").title()
        wedge_sum  = acc.get("wedge", "")[:120]
        score      = acc.get("composite_score", 0)
        tier       = acc.get("tier", "")
        tier_cls   = _tier_class(tier)
        status_html = _status_label(acc)
        plan        = acc.get("plan", {})
        first_action = ""
        if plan.get("warmup_comment"):
            preview = plan["warmup_comment"][:140].replace('"', "&quot;")
            first_action = f'Warm-up comment: "{preview}..."'
        elif plan.get("connection_note"):
            preview = plan["connection_note"][:140].replace('"', "&quot;")
            first_action = f'Connection note: "{preview}..."'

        rows_html += f"""      <tr>
        <td>{i}</td>
        <td>{company}<br><span class="status">{pname}, {ptitle}</span></td>
        <td>{fit}</td>
        <td><span class="trigger">{trigger}</span></td>
        <td class="wedge">{wedge_sum}</td>
        <td class="tier {tier_cls}">{tier} {score}</td>
        <td>{status_html}</td>
        <td class="preview">{first_action}</td>
      </tr>
"""

    dq_html = ""
    for acc in disqualified:
        company = acc.get("company", "")
        reason  = acc.get("disqualify_reason", "outside ICP")
        dq_html += f'<p class="dq"><b>{company}</b> — {reason}</p>\n'

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prospecting engine: outbound queue (dry run)</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font: 15px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; color: #1a1a1a; background: #f6f7f9; margin: 0; padding: 32px; }}
  .wrap {{ max-width: 1040px; margin: 0 auto; }}
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
  .trigger {{ font-size: 12px; display: inline-block; background: #eef2ff; color: #3538cd; border-radius: 5px; padding: 2px 7px; }}
  .wedge {{ color: #475467; font-size: 13px; max-width: 260px; }}
  .preview {{ color: #475467; font-size: 13px; max-width: 300px; }}
  h2 {{ font-size: 16px; margin: 28px 0 10px; }}
  .panel {{ background: #fff; border: 1px solid #e3e6ea; border-radius: 10px; padding: 16px 18px; margin: 0 0 18px; }}
  .dq {{ color: #667085; font-size: 14px; }}
  .foot {{ color: #98a2b3; font-size: 12px; margin-top: 24px; line-height: 1.6; }}
</style>
</head>
<body>
<div class="wrap">
  <h1>Prospecting engine: outbound queue</h1>
  <p class="sub">Dry run. Cold target accounts, sourced from a provided list and public research. {total} accounts in, {n_qual} qualified, {n_disq} disqualified. Nothing has been sent.</p>

  <div class="chips">
    <div class="chip"><b>{total}</b><span>Accounts in</span></div>
    <div class="chip"><b>{n_qual}</b><span>Qualified</span></div>
    <div class="chip"><b>{n_disq}</b><span>Disqualified</span></div>
    <div class="chip"><b>{n_booked}</b><span>Booked</span></div>
    <div class="chip"><b>{n_seq}</b><span>In sequence</span></div>
    <div class="chip"><b>{n_stopped}</b><span>Stopped</span></div>
  </div>

  <table>
    <thead>
      <tr><th>#</th><th>Account / persona</th><th>Fit</th><th>Trigger</th><th>Wedge</th><th>Tier</th><th>Status</th><th>First action (awaiting approval)</th></tr>
    </thead>
    <tbody>
{rows_html}    </tbody>
  </table>

  <h2>Disqualified</h2>
  <div class="panel">
{dq_html}  </div>

  <p class="foot">
    <b>Compliance note.</b> Discovery is from the provided account list and public web research only. No LinkedIn scraping.
    Every LinkedIn action above is staged and awaiting human approval. Nothing has been sent.
    The live send route (--live flag) uses a single sanctioned API (Unipile) with daily caps enforced in code.
    Specific, researched personalization is the compliance strategy: irrelevant volume triggers spam reports.
  </p>
</div>
</body>
</html>
"""
    out_path = output_dir / "prospecting_queue.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def write_state_json(
    qualified: list[dict],
    disqualified: list[dict],
    output_dir: Path,
) -> Path:
    state: dict = {"qualified": [], "disqualified": []}
    for acc in qualified:
        state["qualified"].append({
            "company":        acc.get("company"),
            "persona_name":   acc.get("target_persona_name"),
            "persona_title":  acc.get("target_persona_title"),
            "score":          acc.get("composite_score"),
            "tier":           acc.get("tier"),
            "fit_score":      acc.get("fit_score"),
            "trigger_type":   acc.get("trigger_type"),
            "trigger_strength": acc.get("trigger_strength"),
            "wedge_clarity":  acc.get("wedge_clarity"),
            "lead_hook":      acc.get("lead_hook"),
            "seq_state":      acc.get("_seq_state"),
            "ics_path":       acc.get("_ics_path", ""),
        })
    for acc in disqualified:
        state["disqualified"].append({
            "company":          acc.get("company"),
            "disqualify_reason": acc.get("disqualify_reason"),
        })
    out_path = output_dir / "state.json"
    out_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return out_path


# ── Main pipeline ──────────────────────────────────────────────────────────────

def run(args) -> None:
    dry_run = not args.live

    # Guard: refuse to run if ANTHROPIC_API_KEY is set
    if os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ERROR: ANTHROPIC_API_KEY is set. This repo runs on a Claude subscription, "
            "not an API key. Unset it first:\n  unset ANTHROPIC_API_KEY"
        )
        sys.exit(1)

    config_path   = args.config
    accounts_path = args.accounts
    replies_path  = getattr(args, "replies", None)

    print("=" * 60)
    print("PROSPECTING ENGINE — trigger-based outbound")
    print(f"Mode:     {'dry-run (no sends)' if dry_run else 'LIVE (staged, approval required)'}")
    print(f"Config:   {config_path}")
    print(f"Accounts: {accounts_path}")
    print("=" * 60)

    # ── Stage 1: Ingest ──────────────────────────────────────────────────────
    print("\n[1/8] Ingesting target accounts...")
    cfg      = load_config(config_path)
    accounts = load_accounts(accounts_path)
    replies  = load_replies(replies_path) if replies_path else {}
    print(f"  {len(accounts)} accounts loaded  |  {len(replies)} reply fixtures")

    # ── Stage 2: Trigger detection ───────────────────────────────────────────
    accounts = detect_triggers(accounts, dry_run=dry_run)

    # ── Stage 3: Wedge generation ────────────────────────────────────────────
    accounts = generate_wedges(accounts, dry_run=dry_run)

    # ── Stage 4+5: Score + qualify ───────────────────────────────────────────
    qualified, disqualified = score_and_qualify(accounts, cfg)
    print(f"\n  Summary: {len(qualified)} qualified  |  {len(disqualified)} disqualified")

    # ── Stage 6: Draft engagement plans ─────────────────────────────────────
    qualified = draft_engagement_plans(qualified, cfg)

    # ── Stage 7: State machine + booking ────────────────────────────────────
    out_slug = re.sub(r"[^a-z0-9]+", "_", cfg.get("sender_company", "prospecting").lower()).strip("_")
    output_dir = _REPO_ROOT / "outputs" / f"prospecting_{out_slug}"
    output_dir.mkdir(parents=True, exist_ok=True)

    run_sequence_simulation(qualified, replies, cfg, output_dir, dry_run=dry_run)

    # ── Stage 8: Write outputs ───────────────────────────────────────────────
    print(f"\n[8/8] Writing outputs to {output_dir}/")
    plan_path  = write_prospecting_plan(qualified, disqualified, output_dir)
    queue_path = write_prospecting_queue(qualified, disqualified, output_dir)
    state_path = write_state_json(qualified, disqualified, output_dir)

    print(f"\n  prospecting_plan.md  → {plan_path}")
    print(f"  prospecting_queue.html → {queue_path}")
    print(f"  state.json           → {state_path}")
    if (output_dir / "bookings").exists():
        ics_files = list((output_dir / "bookings").glob("*.ics"))
        for f in ics_files:
            print(f"  bookings/{f.name}")

    print("\n" + "=" * 60)
    n_booked  = sum(1 for a in qualified if a.get("_seq_state", {}).get("state") == "booked")
    n_stopped = sum(1 for a in qualified if a.get("_seq_state", {}).get("state") == "stopped")
    n_seq     = len(qualified) - n_booked - n_stopped
    print(f"Done.  {len(qualified)} qualified  |  {n_booked} booked  |  {n_seq} in sequence  |  {n_stopped} stopped  |  {len(disqualified)} disqualified")
    print("=" * 60)

    if dry_run:
        print("\nAll actions are staged for approval. Nothing was sent.")
    else:
        print("\nLIVE mode: all staged actions require human approval before send.")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prospecting Engine — trigger-based outbound prospecting"
    )
    sub = parser.add_subparsers(dest="command")
    run_p = sub.add_parser("run", help="Run the prospecting pipeline")
    run_p.add_argument("--config",   required=True,  help="Path to prospector_config.md")
    run_p.add_argument("--accounts", required=True,  help="Path to target_accounts.csv")
    run_p.add_argument("--replies",  default=None,   help="Path to replies_fixture.csv (dry-run)")
    run_p.add_argument("--dry-run",  action="store_true", default=True,  help="Dry-run (default)")
    run_p.add_argument("--live",     action="store_true", default=False, help="Live mode (requires UNIPILE_API_KEY)")
    args = parser.parse_args()

    if args.command == "run":
        run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
