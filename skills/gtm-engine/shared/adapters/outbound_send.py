"""
Outbound send adapter — Unipile (LinkedIn + email + calendar).

Default: dry-run stub. Does nothing. Every call returns a dry-run receipt.
Live:    requires UNIPILE_API_KEY in the environment and --live flag.
         Currently a labelled stub with TODOs. Wire in the Unipile SDK
         when you are ready to send.

This adapter is NEVER called in dry-run. The caller guards with:
    if not dry_run and UNIPILE_API_KEY:
        outbound_send.send(...)

Even in live mode, every action must be approved by a human before send.
Daily caps are enforced by the caller before this adapter is reached.
"""

from __future__ import annotations

import os

UNIPILE_API_KEY = os.environ.get("UNIPILE_API_KEY", "")

# Dry-run receipt returned when no real send is made.
_DRY_RUN_RECEIPT = {"status": "dry_run", "sent": False, "message": "Staged for approval. Nothing sent."}


def send_linkedin_comment(*, post_url: str, comment_text: str) -> dict:
    """
    Post a warm-up comment on a prospect's LinkedIn post.

    TODO (live): use Unipile LinkedIn API to post the comment.
                 Endpoint: POST /v1/linkedin/posts/{post_id}/comments
    """
    if not UNIPILE_API_KEY:
        return _DRY_RUN_RECEIPT
    # TODO: implement Unipile call
    raise NotImplementedError("Live LinkedIn comment send not yet wired. Set UNIPILE_API_KEY and implement.")


def send_linkedin_connection(*, profile_url: str, note: str) -> dict:
    """
    Send a LinkedIn connection request with a personalized note.

    TODO (live): use Unipile LinkedIn API.
                 Endpoint: POST /v1/linkedin/connections
    Note must be under 300 characters (enforced by caller).
    """
    if not UNIPILE_API_KEY:
        return _DRY_RUN_RECEIPT
    # TODO: implement Unipile call
    raise NotImplementedError("Live LinkedIn connection send not yet wired.")


def send_linkedin_message(*, profile_url: str, message_text: str) -> dict:
    """
    Send a LinkedIn direct message to a connected prospect.

    TODO (live): use Unipile LinkedIn API.
                 Endpoint: POST /v1/linkedin/messages
    """
    if not UNIPILE_API_KEY:
        return _DRY_RUN_RECEIPT
    # TODO: implement Unipile call
    raise NotImplementedError("Live LinkedIn message send not yet wired.")


def send_email(*, to_address: str, subject: str, body: str, from_name: str, from_address: str) -> dict:
    """
    Send an email follow-up via Unipile.

    TODO (live): use Unipile email API.
                 Endpoint: POST /v1/email/send
    """
    if not UNIPILE_API_KEY:
        return _DRY_RUN_RECEIPT
    # TODO: implement Unipile call
    raise NotImplementedError("Live email send not yet wired.")


def create_calendar_event(*, ics_content: str, attendee_email: str) -> dict:
    """
    Create a calendar event and send an invite.

    TODO (live): use Unipile calendar API or send the .ics via email.
    """
    if not UNIPILE_API_KEY:
        return _DRY_RUN_RECEIPT
    # TODO: implement Unipile call
    raise NotImplementedError("Live calendar invite not yet wired.")
