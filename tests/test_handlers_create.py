import handlers
import pytest

def test_create_booking_missing_fields(ctx):
    # Only provide a subset
    ctx.data.update({"VisitDate": "2025-08-11"})
    ack, body, transform = handlers.handle_create_booking(ctx)
    assert ack == "Missing fields"
    assert "Missing required fields" in body

@pytest.mark.parametrize("party", ["0", "-1", "abc"])
def test_create_booking_invalid_party_size(ctx, party):
    ctx.data.update({
        "VisitDate": "2025-08-11",
        "VisitTime": "12:00:00",
        "PartySize": party,
        "FirstName": "John", "Surname": "Doe", "Email": "john@doe.com"
    })
    ack, body, _ = handlers.handle_create_booking(ctx)
    assert "Invalid party size" in ack or "Invalid party size" in body

@pytest.mark.parametrize("date_str", ["2025/08/11", "11-08-2025"])
def test_create_booking_invalid_date(ctx, date_str):
    ctx.data.update({
        "VisitDate": date_str,
        "VisitTime": "12:00:00",
        "PartySize": 2,
        "FirstName": "John", "Surname": "Doe", "Email": "john@doe.com"
    })
    ack, body, _ = handlers.handle_create_booking(ctx)
    assert ack == "Invalid date"

@pytest.mark.parametrize("time_str", ["12", "12:00:0", "abc"])
def test_create_booking_invalid_time(ctx, time_str):
    ctx.data.update({
        "VisitDate": "2025-08-11",
        "VisitTime": time_str,
        "PartySize": 2,
        "FirstName": "John", "Surname": "Doe", "Email": "john@doe.com"
    })
    ack, body, _ = handlers.handle_create_booking(ctx)
    assert ack == "Invalid time"

@pytest.mark.parametrize("email", ["john", "john@", "john@doe"])
def test_create_booking_invalid_email(ctx, email):
    ctx.data.update({
        "VisitDate": "2025-08-11",
        "VisitTime": "12:00:00",
        "PartySize": 2,
        "FirstName": "John", "Surname": "Doe", "Email": email
    })
    ack, body, _ = handlers.handle_create_booking(ctx)
    assert ack == "Invalid email"

def test_create_booking_success_with_special_requests(monkeypatch, ctx):
    def fake_create(data):
        # ensure optional fields pass through
        assert data["SpecialRequests"] == "Window table please"
        return {
            "status": "confirmed",
            "booking_reference": "ABC1234",
            "restaurant": "TheHungryUnicorn",
            "visit_date": data["VisitDate"],
            "visit_time": data["VisitTime"],
            "party_size": data["PartySize"],
            "customer": {"first_name": "John", "surname": "Doe", "email": "john@doe.com"},
            "special_requests": data["SpecialRequests"],
        }
    monkeypatch.setattr("handlers.tools.create_booking", fake_create)

    ctx.data.update({
        "VisitDate": "2025-08-11",
        "VisitTime": "12:00:00",
        "PartySize": 2,
        "FirstName": "John", "Surname": "Doe", "Email": "john@doe.com",
        "SpecialRequests": "Window table please",
    })
    ack, body, transform = handlers.handle_create_booking(ctx)
    assert "Your reservation is confirmed!" in body
    assert "Special Requests: Window table please" in body
    transform(ctx)
    # resets on success
    assert ctx.data["intent"] is None

def test_create_booking_api_error(monkeypatch, ctx):
    def fake_create(data):
        return {"error": "Unprocessable Entity: Validation errors", "status_code": 422, "details": {"detail": "bad"}}
    monkeypatch.setattr("handlers.tools.create_booking", fake_create)

    ctx.data.update({
        "VisitDate": "2025-08-11",
        "VisitTime": "12:00:00",
        "PartySize": 2,
        "FirstName": "John", "Surname": "Doe", "Email": "john@doe.com",
    })

    ack, body, transform = handlers.handle_create_booking(ctx)
    assert ack == "API Error"
    assert "Unprocessable Entity" in body
    transform(ctx)
    assert ctx.data["intent"] is None
