from typing import Dict
import parser
from state import ConversationContext
from handlers import INTENT_ROUTER

def print_welcome() -> None:
    print("Welcome to The Hungry Unicorn Booking Assistant")
    print("I am able to:")
    print("  1. Check availability")
    print("  2. Create a booking")
    print("  3. Cancel a booking")
    print("  4. Modify a booking\n")
    print("Type 'exit' to quit.\n")

def run_chat() -> None:
    """
    Main chat loop for the booking assistant.
    """
    ctx = ConversationContext()
    print_welcome()

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            print("Agent: Goodbye!")
            break

        ctx.history.append({"role": "user", "content": user_input})

        llm_json: Dict = parser.update_state_with_llm(ctx.history, ctx.data) or {}
        ctx.data = llm_json.get("updated_state", ctx.data)

        next_message = (llm_json.get("next_message") or "").strip()
        if next_message and ctx.data.get("status") != "ready":
            # Only show LLM message when we're still collecting info
            print(f"Agent: {next_message}")

        if ctx.data.get("status") == "ready":
            intent = ctx.data.get("intent")
            handler = INTENT_ROUTER.get(intent)

            
            if not handler:
                print("Agent: Sorry, I didn't understand that action.")
                ctx.reset()
                continue

            ack_for_history, body, transform = handler(ctx)
            formatted_body = body.replace("\n", "\n       ")
            print(f"Agent: {formatted_body}")

            transform(ctx)
            if ack_for_history:
                ctx.history.append({"role": "assistant", "content": ack_for_history})

if __name__ == "__main__":
    try:
        run_chat()
    except KeyboardInterrupt:
        print("\nAgent: Goodbye!")
