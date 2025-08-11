from dataclasses import dataclass, field
from typing import Dict, Optional

def initial_state() -> Dict[str, Optional[str]]:
    """
    Creates the initial conversation state for the booking assistant.
    """
    return {
        "intent": None,
        "VisitDate": None,
        "VisitTime": None,
        "PartySize": None,
        "FirstName": None,
        "Surname": None,
        "Email": None,
        "BookingRef": None,
        "LastBookingRef": None,
        "CancellationReasonId": None,
        "SpecialRequests": None,
        "status": "collecting",
    }

@dataclass
class ConversationContext:
    """
    Maintains the conversation state and message history between the user and the assistant.
    """
    data: Dict[str, Optional[str]] = field(default_factory=initial_state)
    history: list = field(default_factory=list)

    def reset(self) -> None:
        self.data = initial_state()
        self.history.clear()

    def soft_reset(self, preserve_keys: list) -> None:
        preserved = {k: v for k, v in self.data.items() if k in preserve_keys}
        self.reset()
        self.data.update(preserved)
