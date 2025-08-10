import tools
import pytest

def test_handle_response_200(ok_response):
    data = tools.handle_response(ok_response)
    assert data == {"ok": True}

@pytest.mark.parametrize("status,expected_err", [
    (400, "Bad Request"),
    (401, "Unauthorized"),
    (404, "Not Found"),
    (422, "Unprocessable Entity"),
])
def test_handle_response_errors(error_response_factory, status, expected_err):
    resp = error_response_factory(status, payload={"detail": "x"})
    data = tools.handle_response(resp)
    assert "error" in data and expected_err in data["error"]
    assert data["status_code"] == status
    assert "details" in data

def test_handle_response_unexpected(error_response_factory):
    resp = error_response_factory(503)
    data = tools.handle_response(resp)
    assert "error" in data and "Unexpected error" in data["error"]
    assert data["status_code"] == 503

def test_check_availability_calls_requests(monkeypatch, ok_response):
    calls = {}
    def fake_post(url, headers, data):
        calls["url"] = url; calls["headers"] = headers; calls["data"] = data
        return ok_response
    monkeypatch.setattr(tools.requests, "post", fake_post)
    res = tools.check_availability("2025-08-11", 2)
    assert res == {"ok": True}
    assert "/AvailabilitySearch" in calls["url"]

def test_create_booking_calls_requests(monkeypatch, ok_response):
    def fake_post(url, headers, data):
        return ok_response
    monkeypatch.setattr(tools.requests, "post", fake_post)
    res = tools.create_booking({"VisitDate": "2025-08-11"})
    assert res == {"ok": True}

def test_get_booking_calls_requests(monkeypatch, ok_response):
    def fake_get(url, headers):
        return ok_response
    monkeypatch.setattr(tools.requests, "get", fake_get)
    res = tools.get_booking("ABC1234")
    assert res == {"ok": True}
    # no exception

def test_update_booking_calls_requests(monkeypatch, ok_response):
    def fake_patch(url, headers, data):
        return ok_response
    monkeypatch.setattr(tools.requests, "patch", fake_patch)
    res = tools.update_booking("ABC1234", {"PartySize": 4})
    assert res == {"ok": True}

def test_cancel_booking_calls_requests(monkeypatch, ok_response):
    def fake_post(url, headers, data):
        return ok_response
    monkeypatch.setattr(tools.requests, "post", fake_post)
    res = tools.cancel_booking("ABC1234", 1)
    assert res == {"ok": True}
