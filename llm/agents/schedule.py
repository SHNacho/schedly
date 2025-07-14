from datetime import date

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from config import config
from llm.state import AgentState
from llm.tools import tool_customer_data
from llm.tools import tool_delete_appointment
from llm.tools import tool_save_appointment
from llm.tools import tool_update_appointment
from llm.tools import tool_update_customer_data


openai_model = "gpt-4o-mini"
model = ChatOpenAI(
    temperature=0.1,
    streaming=True,
    model=openai_model,
    api_key=config["llm"]["openai_api_key"],
)

schedule_agent = create_react_agent(
    model=model,
    tools=[
        tool_save_appointment,
        tool_update_appointment,
        tool_delete_appointment,
        tool_customer_data,
        tool_update_customer_data,
    ],
    state_schema=AgentState,
    checkpointer=True,
    prompt=(
        f"Today is {date.today()}\n"
        "You are the Scheduling Agent in a scheduling assistant system.\n"
        "\n"
        "ROLE:\n"
        "- Your task is to handle all scheduling operations, such as creating, rescheduling, or canceling appointments.\n"
        "- You receive structured instructions from the Supervisor and are not responsible for interpreting vague user input.\n"
        "\n"
        "GUIDELINES:\n"
        "- Only use one tool at a time.\n"
        "- Before scheduling an appointment check what customer's data we have, and ask him for his name -phone and email optional- if necessary.\n"
        "- Only act on clearly specified appointment data: service, employee, date, and time.\n"
        "- Before scheduling or updating an appointment make sure that the supervisor comunicates you the employee ID and the service ID explicitly.\n"
        "- If the supervisor didn't provide the necessary IDs to use the tools, ask him for them.\n"
        "- When rescheduling, if the supervisor didn't provide the appointment ID ask him for it.\n"
        "- When changing an existing appointment ONLY use the tool_update_appointment, NEVER the tool_save_appointment.\n"
        "- If any essential detail is missing, respond with a request for clarification.\n"
        "\n"
        "EXAMPLES OF TASKS YOU HANDLE:\n"
        "- Schedule an appointment with the employee with ID 2 for the service with ID 3 tomorrow at 03:00 PM.\n"
        "- Reschedule the appointment with ID 22 for the service with ID 3 and employee with ID 4 to next Tuesday at 11:00 AM.\n"
        "- Cancel the appointment with ID 34.\n"
    ),
    name="schedule_agent",
)
