from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from .utils.pretty import pretty_print_messages
from .chat_model import qwen_max, qwen_plus_latest


def book_hotel(hotel_name: str):
    """Book a hotel"""
    return f"Successfully booked a stay at {hotel_name}."


def book_flight(from_airport: str, to_airport: str):
    """Book a flight"""
    return f"Successfully booked a flight from {from_airport} to {to_airport}."


flight_assistant = create_react_agent(
    model=qwen_plus_latest,
    tools=[book_flight],
    prompt="You are a flight booking assistant",
    name="flight_assistant",
)

hotel_assistant = create_react_agent(
    model=qwen_plus_latest,
    tools=[book_hotel],
    prompt="You are a hotel booking assistant",
    name="hotel_assistant",
)

supervisor = create_supervisor(
    agents=[flight_assistant, hotel_assistant],
    model=qwen_plus_latest,
    prompt=(
        "You manage a hotel booking assistant and a"
        "flight booking assistant. Assign work to them."
    ),
).compile()

for chunk in supervisor.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "book a flight from BOS to JFK and a stay at McKittrick Hotel",
            }
        ]
    }
):
    pretty_print_messages(chunk)
