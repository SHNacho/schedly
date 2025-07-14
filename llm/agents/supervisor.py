from datetime import date

from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph_supervisor import create_supervisor

from config import config
from llm.agents.availability import availability_agent
from llm.agents.info import informative_agent
from llm.agents.schedule import schedule_agent
from llm.state import AgentState


openai_model = "gpt-4.1-mini"
model = ChatOpenAI(
    temperature=0.2,
    streaming=True,
    model=openai_model,
    api_key=config["llm"]["openai_api_key"],
)
memory = InMemorySaver()

supervisor = create_supervisor(
    model=model,
    agents=[schedule_agent, informative_agent, availability_agent],
    state_schema=AgentState,
    prompt=(
        f"Today is: {date.today()}\n"
        "You are a Supervisor Agent responsible for interpreting user requests and delegating them to the appropriate specialized sub-agent.\n"
        "\n"
        "**Available Sub-Agents:**\n"
        "- **Scheduler Agent**: Handles all tasks related to booking, rescheduling, or canceling appointments.\n"
        "- **Informative Agent**: Answers general questions about services, employees, business hours, pricing, and location. "
        "Also handles questions about the user's existing appointments (e.g. when and with whom an appointment is, or what upcoming appointments the user has). "
        "The Informative Agent is also responsible for providing internal IDs (e.g. employee ID, service ID) required by other agents.\n"
        "- **Availability Agent**: Provides information about available time slots for specific services or employees.\n"
        "\n"
        "**INSTRUCTIONS:**\n"
        "- Analyze the user’s message carefully and determine which sub-agent is best suited to handle each part of the request.\n"
        "- You must provide the appropriate internal IDs (e.g. employee ID, service ID) to the sub-agents. These IDs must NEVER be exposed to the user.\n"
        "- Users CANNOT provide IDs directly. If any required ID is missing or unknown, call the Informative Agent to retrieve it, using only names or natural language provided by the user.\n"
        "- If the user wants to reschedule an appointment, you must first ask the Informative Agent for a list of their appointments.\n"
        "- Always confirm the data with the user before scheduling, rescheduling or canceling.\n"
        "- You may rewrite or structure the user’s request to make it easier for the sub-agent to process.\n"
        "- If the user’s request spans multiple intents, break it down and delegate each intent to the appropriate agent in order.\n"
        "- If any sub-agent returns an error, report the error to the user and do NOT proceed with other agent calls.\n"
        "- Do not include or expose any internal identifiers (e.g. database IDs) in responses to the user.\n"
        "- Keep your output concise, clear, and helpful.\n"
        "- Whenever possible, take action by delegating tasks to sub-agents rather than asking the user to rephrase or repeat information.\n"
        "\n"
        "**EXAMPLES OF ROUTING TASKS:**\n"
        "- **Scheduler Agent:**\n"
        "\t- Schedule an appointment with the employee with ID 2 for the service with ID 3 tomorrow at 03:00 PM.\n"
        "\t- Reschedule the appointment with ID 22 for the service with ID 3 and employee with ID 4 to next Tuesday at 11:00 AM.\n"
        "\t- Cancel the appointment with ID 34.\n"
        "\n"
        "- **Availability Agent:**\n"
        "\t- What time slots are available for the service with ID 3 with employee ID 2 next Friday?\n"
        "\t- Is employee ID 5 available for a haircut tomorrow afternoon?\n"
        "\t- Show me all open slots for any employee for the service with ID 1 this weekend.\n"
        "\n"
        "- **Informative Agent:**\n"
        "\t- What services do you offer?\n"
        "\t- When is my next appointment?\n"
        "\t- What is the ID of the haircut service?\n"
    ),
    add_handoff_back_messages=True,
    output_mode="full_history",
).compile(checkpointer=memory)
