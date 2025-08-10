from typing import Dict

def fmt_booking_header(resp: Dict) -> list:
    """
    Formats booking details into a list of readable strings.
    """
    customer = resp.get("customer", {}) or {}
    lines = [
        f"Reference: {resp.get('booking_reference')}",
        f"Name: {customer.get('first_name', '')} {customer.get('surname', '')}".rstrip(),
        f"Email: {customer.get('email', 'Not Provided')}",
        f"Restaurant: {resp.get('restaurant')}",
        f"Date: {resp.get('visit_date')}",
        f"Time: {resp.get('visit_time')}",
        f"Party Size: {resp.get('party_size')}",
    ]
    if resp.get("special_requests"):
        lines.append(f"Special Requests: {resp.get('special_requests')}")
    return lines

def fmt_updates(updates: Dict) -> str:
    """
    Formats updated booking fields into a readable string.
    """
    return ", ".join(f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in updates.items())
