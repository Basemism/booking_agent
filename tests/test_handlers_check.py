import handlers

def test_check_availability_success(monkeypatch, ctx):
    def fake_api(date, size, channel_code="ONLINE"):
        return {
            "visit_date": date,
            "party_size": size,
            "available_slots": [
                {"time": "12:00:00", "available": True},
                {"time": "12:30:00", "available": True},
                {"time": "13:00:00", "available": False},
            ]
        }
    monkeypatch.setattr("handlers.tools.check_availability", fake_api)
    ctx.data.update({"VisitDate": "2025-08-11", "PartySize": 2})
    ack, body, transform = handlers.handle_check_availability(ctx)
    assert "available at: 12:00:00, 12:30:00" in body
    assert "fully booked: 13:00:00" in body
    # transform should reset on success
    transform(ctx)
    assert ctx.data["intent"] is None

def test_check_availability_api_error(monkeypatch, ctx):
    def fake_api(date, size, channel_code="ONLINE"):
        return {"error": "Not Found: Restaurant or booking not found", "status_code": 404, "details": {"detail": "x"}}
    monkeypatch.setattr("handlers.tools.check_availability", fake_api)
    ctx.data.update({"VisitDate": "2025-08-11", "PartySize": 2})
    ack, body, transform = handlers.handle_check_availability(ctx)
    assert ack == "API Error"
    assert "Not Found" in body
    transform(ctx)
    # resets on error
    assert ctx.data["intent"] is None
