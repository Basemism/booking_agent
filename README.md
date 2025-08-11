![Tests](https://github.com/Basemism/booking_agent/actions/workflows/tests.yml/badge.svg)

# Restaurant Booking Assistant

## Overview

The Restaurant Booking Assistant is a Python-based application designed to facilitate restaurant reservations. It provides a user-friendly interface for customers to book tables, manage their reservations, and receive updates about their bookings.

## Getting Started

To get started with the Restaurant Booking Assistant, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/Basemism/booking_agent.git
   cd booking_agent
   ```
2. Set up your environment variables:
   Create a `.env` file in the root directory and add your API keys, Bearer tokens, and other configuration settings.
    ```env
    BASE_URL=http://localhost:8547
    RESTAURANT_NAME=TheHungryUnicorn
    BEARER_TOKEN=YOUR_TOKEN
    OPENAI_API_KEY=YOUR_API_KEY
    ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the mock booking server:
    ```bash
    git clone https://github.com/AppellaAI/Restaurant-Booking-Mock-API-Server
    cd Restaurant-Booking-Mock-API-Server
    python -m app
    ```
5. Start the assistant:
   ```bash
   python main.py
   ```
### Usage
Example conversation:

    Welcome to The Hungry Unicorn Booking Assistant
    I am able to:
    1. Check availability
    2. Create a booking
    3. Cancel a booking
    4. Modify a booking

    Type 'exit' to quit.

    You: check availability for tomorrow for 2 people
    Agent: On 2025-08-11, we have tables for 2 available at: 12:00:00, 19:00:00.

    You: book for 19:00, John Doe, john@doe.com
    Agent: Your reservation is confirmed!
        Reference: ABC1234
        Name: John Doe
        Email: john@doe.com
        Restaurant: TheHungryUnicorn
        Date: 2025-08-11
        Time: 19:00:00
        Party Size: 2
        Status: confirmed

## Design Rationale
The assistant was designed with the following goals in mind:
1. **Reliability**: It should handle every happy path and edge case gracefully.
2. **Maintainability & Extensibility**: The codebase should be easy to understand, modify, and extend with new features or integrations without major refactoring.
3. **User-Centric Design**: The assistant should prioritise user needs and provide a seamless booking experience.

### 1. Intent Router + Modular Handlers
The assistant uses an intent router pattern:
- State tracking is centralised in `ConversationContext` (in [`state.py`](state.py)), storing booking data and message history.
- Intents are mapped to specific handler functions in [`handlers.py`](handlers.py).
- Handlers encapsulate the logic for each intent, including:
  - Preflight checks to validate user input.
  - API calls to the booking service via [`tools.py`](tools.py).
  - Formatting of API responses for user-friendly output.
  - State transformation for conversation context updates.

By keeping such issues apart, you can add a new features without modifying irrelevant code. You would change the LLM prompt in [`parser.py`](parser.py), add the new intent, construct its handler, and connect it to the router.

### 2. Language Model Role
The LLM (via [`parser.py`](parser.py)) is not allowed to call APIs directly or format results. Its sole responsibility is:

- Merging user inputs into the current structured state

- Inferring the intent when missing

- Deciding if the state is “collecting” or “ready”

- Producing the next message when more details are needed

The LLM’s output is strict JSON, parsed into ctx.data. Once the state is “ready,” execution is passed to the relevant handler.

Because all final output is handled by the specified functions, this separation stops the LLM from returning responses that are either incomplete or incorrectly structured.  It also implies that error handling, validation, and authentication for APIs remain within Python code that is under control.

### 3. Preflight Validation
Even though the LLM collects structured fields, the handlers re-validate inputs before calling the API:
- Dates must match `YYYY-MM-DD`
- Times must match `HH:MM` or `HH:MM:SS`
- Party size must be a positive integer
- Email must be in a basic valid form

This is important because it protects the API from bad/accidental data and strengthens the system against language model errors.  It also ensures that API authentication, validation, and error handling are all contained within regulated Python code.

### 4. API Layer and Error Handling
All HTTP calls are routed through [`tools.py`](tools.py), which:
- Reads config from .env for BASE_URL, RESTAURANT_NAME, and BEARER_TOKEN
- Wraps requests calls in a `handle_response()` that:
    - Parses JSON
    - Switches on status_code to return consistent error dicts (200, 400, 401, 404, 422, others)
- Lets handlers check for if "error" in resp and respond accordingly

A helper `format_api_response()` in [`handlers.py`](handlers.py) takes a success formatter and applies the same error handling across all intents.

### 5. Formatters
[`formatters.py`](formatters.py) contains functions like:
- `fmt_booking_header()` - formats booking details into consistent bullet lists
- `fmt_updates()` - formats update payloads for user readability

Consistent formatting helps the assistant’s tone stay uniform and professional, while also making it easier to change the output style in one place.    

### 6. Security

- All secrets and environment-specific config are in `.env`
- Bearer token is never hardcoded
- Validation guards against invalid/malicious input before hitting the API
- Only whitelisted fields are passed to the API

This keeps the API surface area small and reduces the risk of exposing sensitive data.

### 7. Limitations and Potential Improvements
While the assistant is functional, it has some limitations that could be addressed in future iterations:
- Volatile in-memory context - State resets when the process ends; no persistence across sessions. We could save state to disk or DB to resume conversations after restarts.

- Terminal-only interaction - No support for web, mobile, or chat platform interfaces. Integrate with web chat or messaging apps to expand accessibility.

- LLM-only state manager - Entirely dependent on the LLM for intent detection and slot filling; no rule-based fallback. We could implement a hybrid approach that combines LLM capabilities with rule-based as a fallback when the LLM is unavailable.

- One-shot booking validation - Does not re-confirm booking details with the user once all fields are collected unless prompted. To address this, we could implement a review step before finalising bookings.

### 8. Testing

The pytest suite covers:
- API error handling
- Input validation
- All intent handlers
- Formatting

## Video Demo

<!DOCTYPE html>
<html>
<body>
  <iframe src="https://drive.google.com/file/d/14_5sh3OfAbLyhdyWTDQ4oiWCtP_rx6e4/preview" allowfullscreen="allowfullscreen"></iframe>
</body>
</html>