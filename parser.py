import json
from autogen import AssistantAgent
from datetime import date

nlu_agent = AssistantAgent(
    name="state_manager",
    llm_config={"model": "gpt-4o"},
    system_message="You are a restaurant booking assistant's state manager."
)

def update_state_with_llm(conversation_history, current_state):
    """
    Updates the structured booking state by merging new details from the latest
    user message using a language model.

    Args:
        conversation_history (list): The full sequence of role/content messages exchanged so far.
        current_state (dict): The current known booking details and status.

    Returns:
        dict: A JSON object with:
              - "updated_state": the merged booking state after interpreting the latest input
              - "next_message": what the assistant should say next (question or confirmation)
    """

    today = date.today().isoformat()

    prompt = f"""
    You manage restaurant bookings and maintain a JSON state across turns.

    Today's date: {today}
    Day of the week: {date.today().strftime('%A')}

    STRICT RULES:
    - ALWAYS preserve previously-known fields unless the user explicitly changes them.
    - If the user provides a relative date (e.g., "tomorrow", "next Friday"),
      convert it to an absolute YYYY-MM-DD using today's date.
    - If the user provides time in 12-hour format (e.g., "2pm"),
      convert it to 24-hour HH:MM:SS.
    - Convert party size words or phrases ("four", "for 4") to an integer (4).
    - For UPDATE flows: when the user requests a change (e.g., "move to the next day",
      "change time to 8pm", "make it 6 people"), OVERWRITE the corresponding existing field
      with the normalized value.
    - In UPDATE flows, if the user says "no" or "that's all" or similar after a change,
      mark status as 'ready' and proceed with the update, even if no new fields are provided.
    - Only ask for fields that are still missing. Do NOT re-ask for fields already present.
    - If all required fields for the current intent are present, set "status": "ready" and
      write a short confirmation in "next_message".
    - If something is missing, set "status": "collecting" and ask ONE concise, helpful question
      in "next_message".

    IMPORTANT CLARIFICATION:
    - Do NOT prompt for optional fields.
    - Do NOT confirm or imply that an action (like checking availability or making a booking) has been completed.
    - Your job is ONLY to collect and normalize information, update the state, and ask for missing details.
    - If all required fields are present, set "status": "ready" and in "next_message" simply confirm the details you have collected and state that you are ready to proceed, but do NOT say the action is done or checked.
    - Do NOT mention results or outcomes (e.g., "I have checked availability", "Booking is confirmed", "No slots available"). Leave that to downstream systems.
    - Your confirmation should be neutral, e.g., "I have all the details for your request to check availability for 4 people on 2026-08-20 at 12:00. I will proceed with checking availability." or "Ready to proceed with your booking request for 4 people on 2026-08-20 at 12:00."

    Intents and required fields:
      check_availability -> VisitDate, PartySize
      create_booking    -> VisitDate, VisitTime, PartySize, FirstName, Surname, Email, [Optional: SpecialRequests, Mobile]
      get_booking       -> BookingRef
      update_booking    -> BookingRef and at least one of: VisitDate, VisitTime, PartySize, SpecialRequests
      cancel_booking    -> BookingRef, CancellationReasonId
      greeting, unknown

    CancellationReasonId:
      1: Customer Request
      2: Restaurant Closure
      3: Weather
      4: Emergency
      5: No Show

    Conversation so far (array of {{role, content}}):
    {json.dumps(conversation_history, indent=2)}

    Current state (JSON):
    {json.dumps(current_state, indent=2)}

    Your task:
    1) Infer or confirm the intent (if missing).
    2) Merge new information from the latest user message into the state.
    3) Normalize dates/times/party size as per rules.
    4) Decide whether status is 'collecting' or 'ready'.
    5) Produce the assistant's next message (either a follow-up question or a neutral confirmation that you are ready to proceed, but NOT that the action is done).

    NEVER RESPOND IN A MARKDOWN CODE BLOCK, I.E. ```json ```
    Respond ONLY in valid JSON:

    {{
      "updated_state": {{ ...merged and updated state... }},
      "next_message": "what the assistant should say next"
    }}
    """

    raw = nlu_agent.generate_reply(messages=[{"role": "user", "content": prompt}])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        print(raw)
        return {
            "updated_state": current_state,
            "next_message": "Sorry, I couldn’t parse that. Could you rephrase?"
            
        }
