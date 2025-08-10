from formatters import fmt_booking_header, fmt_updates

def test_fmt_booking_header_includes_all():
    resp = {
        "booking_reference": "XYZ9999",
        "restaurant": "TheHungryUnicorn",
        "visit_date": "2025-08-11",
        "visit_time": "12:00:00",
        "party_size": 2,
        "special_requests": "Window seat",
        "customer": {"first_name": "Jane", "surname": "Doe", "email": "jane@doe.com"}
    }
    lines = fmt_booking_header(resp)
    joined = "\n".join(lines)
    assert "Reference: XYZ9999" in joined
    assert "Name: Jane Doe" in joined
    assert "Email: jane@doe.com" in joined
    assert "Restaurant: TheHungryUnicorn" in joined
    assert "Date: 2025-08-11" in joined
    assert "Time: 12:00:00" in joined
    assert "Party Size: 2" in joined
    assert "Special Requests: Window seat" in joined

def test_fmt_updates():
    updates = {"visit_date": "2025-08-12", "party_size": 4}
    s = fmt_updates(updates)
    assert "Visit date: 2025-08-12" in s
    assert "Party size: 4" in s
