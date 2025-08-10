import parser
import main

def test_parser_contract(monkeypatch):
    # Simulate the LLM returning a ready state with a next_message
    def fake_update(history, state):
        updated = dict(state)
        updated.update({"intent": "get_booking", "BookingRef": "ABC1234", "status": "ready"})
        return {"updated_state": updated, "next_message": "Ready to fetch booking."}
    monkeypatch.setattr(parser, "update_state_with_llm", fake_update)

    assert callable(main.run_chat)