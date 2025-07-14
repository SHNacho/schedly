from datetime import date

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from config import config
from llm.state import AgentState
from llm.tools import tool_list_customer_appointments
from llm.tools import tool_list_employees
from llm.tools import tool_list_services


openai_model = "gpt-4o-mini"
model = ChatOpenAI(
    temperature=0.1,
    streaming=True,
    model=openai_model,
    api_key=config["llm"]["openai_api_key"],
)

informative_agent = create_react_agent(
    model=model,
    tools=[tool_list_services, tool_list_employees, tool_list_customer_appointments],
    state_schema=AgentState,
    checkpointer=True,
    prompt=(
        f"Today is {date.today()}\n"
        "You are the Informative Agent in a scheduling assistant system.\n"
        "\n"
        "ROLE:\n"
        "- You help clients giving information about their appointments.\n"
        "- You answer questions related to the services offered, employee profiles, working hours, pricing, location, and other general information.\n"
        "- You help supervisor providing internal IDs (i.e. Employee ID, Service ID, Appointment ID, ...)\n"
        "- You don't help with availability checking. For this exists the availability sub-agent.\n"
        "\n"
        "GUIDELINES:\n"
        "- Be concise, helpful, and polite.\n"
        "- If you don’t have enough information to answer, respond with 'I’m not sure about that' or escalate to the Supervisor.\n"
        "- ALWAYS provide the IDs to the supervisor.\n"
        "\n"
        "EXAMPLES OF TASKS YOU HANDLE:\n"
        "- 'What services do you offer?'\n"
        "- 'Can you tell me more about Laura, the stylist?'\n"
        "- 'What are your opening hours?'\n"
        "- 'Where are you located?'\n"
        "- 'What is the ID of the haircut service?'\n"
    ),
    name="informative_agent",
)
