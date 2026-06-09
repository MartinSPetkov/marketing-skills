"""
Sequence state machine for outbound_engine and prospecting_engine.

Both tools share this module so the state transitions, reply handling, and
daily-cap enforcement are implemented once.

States
------
new              Just ingested; nothing sent.
warmup           Warm-up comment staged (only when a recent post is available).
connection_sent  Connection request staged.
connected        Connection accepted (simulated in dry-run).
msg1             Message 1 staged.
msg2             Message 2 staged (no reply to msg1).
email            Email follow-up staged (no reply to msg2).
booked           Terminal — positive reply received; meeting booked.
stopped          Terminal — negative reply; sequence ended politely.
disqualified     Terminal — disqualified at scoring stage.

Usage
-----
from shared.sequence import SequenceState, simulate_dry_run

state = SequenceState(name="Priya Shah", has_warmup=True)
state.advance(reply_sentiment="positive")   # → booked

accounts = simulate_dry_run(qualified_accounts, replies_by_name, has_warmup_fn)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta


# ── States ─────────────────────────────────────────────────────────────────────

TOUCH_ORDER = ["warmup", "connection_sent", "msg1", "msg2", "email"]
TERMINAL_STATES = {"booked", "stopped", "disqualified"}

# Day offsets for each touch (relative to Day 0 = warm-up or first action).
# Callers override via sequence_def from config.
DEFAULT_DAY_OFFSETS: dict[str, int] = {
    "warmup":           0,
    "connection_sent":  2,
    "msg1":             3,
    "msg2":             6,
    "email":           10,
}


@dataclass
class SequenceState:
    """Tracks one lead or account through its outbound sequence."""
    name: str
    state: str = "new"
    current_touch: str = ""
    outcome: str = ""
    reply_text: str = ""
    meeting_file: str = ""
    notes: list[str] = field(default_factory=list)

    @property
    def is_terminal(self) -> bool:
        return self.state in TERMINAL_STATES

    @property
    def is_booked(self) -> bool:
        return self.state == "booked"

    @property
    def is_stopped(self) -> bool:
        return self.state == "stopped"

    def advance(self, reply_sentiment: str = "none", skip_warmup: bool = False) -> "SequenceState":
        """
        Advance the state machine by one step based on reply_sentiment:
          "positive" → booked (terminal)
          "negative" → stopped (terminal)
          "none"     → move to the next touch in the sequence

        skip_warmup=True skips the warmup state (used when no recent post).
        Returns self for chaining.
        """
        if self.is_terminal:
            return self

        if reply_sentiment == "positive":
            self.state = "booked"
            self.outcome = "positive_reply"
            return self

        if reply_sentiment == "negative":
            self.state = "stopped"
            self.outcome = "negative_reply"
            return self

        # No reply — move to next touch
        _next = _next_state(self.state, skip_warmup=skip_warmup)
        self.state = _next
        self.current_touch = _next
        return self

    def disqualify(self, reason: str = "") -> "SequenceState":
        self.state = "disqualified"
        self.outcome = reason or "disqualified"
        return self

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "state": self.state,
            "current_touch": self.current_touch,
            "outcome": self.outcome,
            "reply_text": self.reply_text,
            "meeting_file": self.meeting_file,
            "notes": self.notes,
        }


def _next_state(current: str, skip_warmup: bool = False) -> str:
    """Return the next non-terminal state after current."""
    order = [t for t in TOUCH_ORDER if not (skip_warmup and t == "warmup")]
    try:
        idx = order.index(current)
        if idx + 1 < len(order):
            return order[idx + 1]
        return "stopped"   # exhausted sequence with no reply
    except ValueError:
        if current == "new":
            return "warmup" if not skip_warmup else "connection_sent"
        return "stopped"


# ── Dry-run simulator ─────────────────────────────────────────────────────────

def simulate_dry_run(
    accounts: list[dict],
    replies: dict[str, dict],
    *,
    name_key: str = "persona_name",
    has_warmup_fn=None,
    sequence_def: dict[str, int] | None = None,
    caps: dict[str, int] | None = None,
    base_date: date | None = None,
) -> list[SequenceState]:
    """
    Simulate the full sequence for each qualified account in dry-run.

    Parameters
    ----------
    accounts     : list of account dicts (must have name_key set)
    replies      : {name: {"touch": str, "reply_text": str, "sentiment": str}}
    name_key     : which field in account holds the persona name
    has_warmup_fn: callable(account) -> bool — True if account has a recent post
    sequence_def : day offsets dict overriding DEFAULT_DAY_OFFSETS
    caps         : {"comments": int, "connections": int, "messages": int}
    base_date    : simulation start date (defaults to today)

    Returns a list of SequenceState objects in the same order as accounts.
    """
    day_offsets = {**DEFAULT_DAY_OFFSETS, **(sequence_def or {})}
    caps = caps or {"comments": 15, "connections": 20, "messages": 30}
    base = base_date or date.today()
    cap_tracker: dict[str, dict[str, int]] = {}  # date_str → {touch: count}

    if has_warmup_fn is None:
        has_warmup_fn = lambda a: bool(a.get("recent_post_excerpt", "").strip())

    states: list[SequenceState] = []

    for account in accounts:
        persona_name = account.get(name_key, account.get("name", "unknown"))
        reply_info = replies.get(persona_name, {})
        reply_touch = reply_info.get("touch", "")
        reply_sentiment = reply_info.get("sentiment", "none")
        reply_text = reply_info.get("reply_text", "")

        skip_warmup = not has_warmup_fn(account)
        st = SequenceState(name=persona_name)

        # Walk through touches in order
        touches = [t for t in TOUCH_ORDER if not (skip_warmup and t == "warmup")]
        for touch in touches:
            if st.is_terminal:
                break

            # Enforce daily caps
            touch_date = (base + timedelta(days=day_offsets.get(touch, 0))).isoformat()
            day = cap_tracker.setdefault(touch_date, {})
            cap_key = _cap_key(touch)
            day[cap_key] = day.get(cap_key, 0) + 1

            cap_limit = caps.get(cap_key, 999)
            if day[cap_key] > cap_limit:
                st.notes.append(f"Cap hit on {touch} ({touch_date}); deferred.")
                continue

            # Is this the touch the fixture says they replied on?
            sentiment = reply_sentiment if touch == reply_touch else "none"
            st.current_touch = touch
            st.advance(reply_sentiment=sentiment, skip_warmup=skip_warmup)

        if st.is_booked:
            st.reply_text = reply_text
            st.meeting_file = f"bookings/booking_{_slug(persona_name)}.ics"

        states.append(st)

    return states


def _cap_key(touch: str) -> str:
    if touch == "warmup":
        return "comments"
    if touch == "connection_sent":
        return "connections"
    return "messages"


def _slug(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


# ── ICS generator ──────────────────────────────────────────────────────────────

def make_ics(
    *,
    persona_name: str,
    company: str,
    sender_name: str,
    sender_email: str,
    attendee_email: str,
    booking_link: str,
    summary_line: str,
    description: str,
    meeting_date: date,
    duration_minutes: int = 30,
) -> str:
    """Return a VCALENDAR .ics string for a booked meeting."""
    uid = f"{_slug(persona_name)}-{meeting_date.isoformat()}@gtm-engine"
    dt_start = f"{meeting_date.strftime('%Y%m%d')}T150000Z"
    dt_end_d = meeting_date
    # Add duration
    from datetime import datetime as _dt, timedelta as _td
    dt_end = (_dt.strptime(dt_start, "%Y%m%dT%H%M%SZ") + _td(minutes=duration_minutes)).strftime("%Y%m%dT%H%M%SZ")
    dtstamp = _dt.utcnow().strftime("%Y%m%dT%H%M%SZ")

    return (
        "BEGIN:VCALENDAR\r\n"
        "VERSION:2.0\r\n"
        "PRODID:-//GTM Engine//Prospecting Engine//EN\r\n"
        "CALSCALE:GREGORIAN\r\n"
        "METHOD:REQUEST\r\n"
        "BEGIN:VEVENT\r\n"
        f"UID:{uid}\r\n"
        f"DTSTAMP:{dtstamp}\r\n"
        f"DTSTART:{dt_start}\r\n"
        f"DTEND:{dt_end}\r\n"
        f"SUMMARY:{summary_line}\r\n"
        f"DESCRIPTION:{description} Booking link: {booking_link}\r\n"
        f"LOCATION:{booking_link}\r\n"
        f"ORGANIZER;CN={sender_name}:mailto:{sender_email}\r\n"
        f"ATTENDEE;CN={persona_name};RSVP=TRUE:mailto:{attendee_email}\r\n"
        "STATUS:CONFIRMED\r\n"
        "SEQUENCE:0\r\n"
        "END:VEVENT\r\n"
        "END:VCALENDAR\r\n"
    )
