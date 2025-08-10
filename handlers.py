from typing import Callable, Dict, Tuple
import re
import tools

from state import ConversationContext
from formatters import fmt_booking_header, fmt_updates
from constants import *

# Type alias for handler return value
HandlerResult = Tuple[str, str, Callable[[ConversationContext], None]]

def format_api_response(resp: dict, success_formatter: Callable[[dict], str], reset_on_error: bool = True) -> HandlerResult:
    """
    Centralised API response handling for all intents.
    """
    if isinstance(resp, dict) and "error" in resp:
        details = resp.get("details")
        msg = resp["error"]
        if details:
            msg += f"\nDetails: {details}"
        def transform(c: ConversationContext) -> None:
            if reset_on_error:
                c.reset()
        return ("API Error", msg, transform)
    return ("", success_formatter(resp), lambda c: None)

def handle_check_availability(ctx: ConversationContext) -> HandlerResult:
    """
    Handle the check availability intent.
    """

    resp = tools.check_availability(ctx.data["VisitDate"], ctx.data["PartySize"])

    def success_formatter(data: dict) -> str:
        available = [s["time"] for s in data.get("available_slots", []) if s.get("available")]
        unavailable = [s["time"] for s in data.get("available_slots", []) if not s.get("available")]

        body_parts = []
        if available:
            body_parts.append(
                f"On {data.get('visit_date')}, we have tables for {data.get('party_size')} available at: {', '.join(available)}."
            )
        else:
            body_parts.append(
                f"Sorry, there are no available slots for {data.get('party_size')} on {data.get('visit_date')}."
            )
        if unavailable:
            body_parts.append(f"The following times are fully booked: {', '.join(unavailable)}.")
        return "\n".join(body_parts)

    return format_api_response(resp, success_formatter, reset_on_error=True)

def handle_create_booking(ctx: ConversationContext) -> HandlerResult:
    """
    Handle the create booking intent.
    """

    required = ["VisitDate", "VisitTime", "PartySize", "FirstName", "Surname", "Email"]
    missing = [k for k in required if not ctx.data.get(k)]
    if missing:
        msg = "Missing required fields: " + ", ".join(missing) + ". Please provide those to proceed."
        return ("Missing fields", msg, lambda c: None)

    try:
        party_size = int(str(ctx.data["PartySize"]).strip())
        if party_size <= 0:
            raise ValueError
    except Exception:
        return ("Invalid party size", "Party size must be a positive integer (e.g., 2).", lambda c: None)

    visit_date = str(ctx.data["VisitDate"]).strip()
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", visit_date):
        return ("Invalid date", "VisitDate must be in YYYY-MM-DD format.", lambda c: None)

    visit_time = str(ctx.data["VisitTime"]).strip()
    if re.match(r"^\d{2}:\d{2}$", visit_time):
        visit_time += ":00"
    if not re.match(r"^\d{2}:\d{2}:\d{2}$", visit_time):
        return ("Invalid time", "VisitTime must be HH:MM or HH:MM:SS (24-hour).", lambda c: None)

    email = str(ctx.data["Email"]).strip()
    if "@" not in email or "." not in email.split("@")[-1]:
        return ("Invalid email", "Please provide a valid email address (e.g., name@example.com).", lambda c: None)

    payload = {
        "VisitDate": visit_date,
        "VisitTime": visit_time,
        "PartySize": party_size,
        "ChannelCode": "ONLINE",
        "Customer[FirstName]": str(ctx.data["FirstName"]).strip(),
        "Customer[Surname]": str(ctx.data["Surname"]).strip(),
        "Customer[Email]": email,
    }

    if ctx.data.get("SpecialRequests"):
        payload["SpecialRequests"] = str(ctx.data["SpecialRequests"]).strip()

    if ctx.data.get("Mobile"):
        payload["Mobile"] = str(ctx.data["Mobile"]).strip()

    resp = tools.create_booking(payload)

    def success_formatter(data: dict) -> str:
        return "\n".join(
            ["Your reservation is confirmed!"] + fmt_booking_header(data) + [f"Status: {data.get('status')}"]
        )

    ack, body, base_transform = format_api_response(resp, success_formatter, reset_on_error=True)

    def transform(c: ConversationContext) -> None:
        base_transform(c)
        if not (isinstance(resp, dict) and "error" in resp):
            c.reset()

    return (ack or "I've created your booking.", body, transform)

def handle_get_booking(ctx: ConversationContext) -> HandlerResult:
    """
    Handle the get booking intent.
    """

    resp = tools.get_booking(ctx.data["BookingRef"])

    def success_formatter(data: dict) -> str:
        body_parts = ["Here are your booking details:"]
        body_parts.extend(fmt_booking_header(data))
        body_parts.append(f"Status: {data.get('status')}")
        if data.get("cancellation_reason"):
            body_parts.append(f"Cancellation Reason: {data.get('cancellation_reason')}")
        return "\n".join(body_parts)

    return format_api_response(resp, success_formatter, reset_on_error=True)

def handle_update_booking(ctx: ConversationContext) -> HandlerResult:
    """
    Handle the update booking intent.
    """

    booking_ref = (ctx.data.get("BookingRef") or "").strip()
    if not booking_ref:
        return ("Missing booking reference",
                "Please provide your booking reference to update your reservation.",
                lambda c: None)

    candidate = {
        "VisitDate": ctx.data.get("VisitDate"),
        "VisitTime": ctx.data.get("VisitTime"),
        "PartySize": ctx.data.get("PartySize"),
        "SpecialRequests": ctx.data.get("SpecialRequests"),
    }

    updates: Dict[str, str] = {}

    if candidate["VisitDate"]:
        visit_date = str(candidate["VisitDate"]).strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", visit_date):
            return ("Invalid date", "VisitDate must be in YYYY-MM-DD format.", lambda c: None)
        updates["VisitDate"] = visit_date

    if candidate["VisitTime"]:
        visit_time = str(candidate["VisitTime"]).strip()
        if re.match(r"^\d{2}:\d{2}$", visit_time):
            visit_time += ":00"
        if not re.match(r"^\d{2}:\d{2}:\d{2}$", visit_time):
            return ("Invalid time", "VisitTime must be HH:MM or HH:MM:SS (24-hour).", lambda c: None)
        updates["VisitTime"] = visit_time

    if candidate["PartySize"] not in (None, ""):
        try:
            party_size = int(str(candidate["PartySize"]).strip())
            if party_size <= 0:
                raise ValueError
        except Exception:
            return ("Invalid party size", "Party size must be a positive integer (e.g., 2).", lambda c: None)
        updates["PartySize"] = str(party_size)

    if candidate["SpecialRequests"] not in (None, ""):
        sr = str(candidate["SpecialRequests"]).strip()
        if len(sr) > 500:
            return ("Special requests too long",
                    "Please keep special requests under 500 characters.",
                    lambda c: None)
        if sr:
            updates["SpecialRequests"] = sr

    if not updates:
        return ("No changes detected",
                "Tell me what you'd like to change (date, time, party size, or special requests).",
                lambda c: None)

    resp = tools.update_booking(booking_ref, updates)

    def success_formatter(data: dict) -> str:
        parts = [f"Your booking {data.get('booking_reference')} at {data.get('restaurant')} has been updated."]
        if data.get("updates"):
            parts.append(f"Updated details: {fmt_updates(data['updates'])}.")
        msg = data.get("message")
        if msg:
            parts.append(msg)
        return "\n".join(parts)

    ack, body, base_transform = format_api_response(resp, success_formatter, reset_on_error=False)

    def transform(c: ConversationContext) -> None:
        base_transform(c)
        if not (isinstance(resp, dict) and "error" in resp):
            c.soft_reset(preserve_keys=["BookingRef"])
            c.history.append({"role": "assistant", "content": "I've updated your booking."})
            c.data["intent"] = INTENT_UPDATE

    return (ack or "I've updated your booking.", body, transform)

def handle_cancel_booking(ctx: ConversationContext) -> HandlerResult:
    """
    Handle the cancel booking intent.
    """

    resp = tools.cancel_booking(ctx.data["BookingRef"], ctx.data["CancellationReasonId"])

    def success_formatter(data: dict) -> str:
        return (
            f"Your booking {data.get('booking_reference')} at {data.get('restaurant')} has been cancelled "
            f"due to '{data.get('cancellation_reason')}'.\n{data.get('message')}"
        )

    return format_api_response(resp, success_formatter, reset_on_error=True)

# Router mapping
INTENT_ROUTER: Dict[str, Callable[[ConversationContext], HandlerResult]] = {
    INTENT_CHECK: handle_check_availability,
    INTENT_CREATE: handle_create_booking,
    INTENT_GET: handle_get_booking,
    INTENT_UPDATE: handle_update_booking,
    INTENT_CANCEL: handle_cancel_booking,
}
