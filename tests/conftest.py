import pytest
from state import ConversationContext

import warnings
warnings.filterwarnings("ignore")


@pytest.fixture
def ctx():
    # Fresh context per test
    return ConversationContext()

@pytest.fixture
def ok_response():
    class Resp:
        status_code = 200
        def json(self):
            return {"ok": True}
        text = '{"ok": true}'
    return Resp()

@pytest.fixture
def error_response_factory():
    def _make(status, payload=None, resp_text=None):
        class Resp:
            status_code = status
            def json(self):
                return payload if payload is not None else {"detail": f"status={status}"}
            text = resp_text or f"err {status}"
        return Resp()
    return _make
