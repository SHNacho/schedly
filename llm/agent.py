import json
from datetime import date

from config import config
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt import ToolNode
from llm.state import AgentState
from llm.tools import tool_available_hours
from llm.tools import tool_delete_appointment
from llm.tools import tool_list_customer_appointments
from llm.tools import tool_list_services
from llm.tools import tool_list_stylists
from llm.tools import tool_save_appointment
from llm.tools import tool_stylist_available_hours
from llm.tools import tool_update_appointment
from llm.tools import tool_save_customer
from llm.utils import print_stream


# Instantiate model
openai_model = "gpt-4o-mini"
model = ChatOpenAI(
    temperature=0.1,
    streaming=True,
    model=openai_model,
    api_key=config["llm"]["openai_api_key"],
)
# Instantiate tools
tools = [
    tool_available_hours,
    tool_delete_appointment,
    tool_list_services,
    tool_list_stylists,
    tool_list_customer_appointments,
    tool_save_appointment,
    tool_save_customer,
    #tool_stylist_available_hours,
    tool_update_appointment,
]
# Bind tools to the model
model = model.bind_tools(tools)

### Nodes ###

# Define our tool node
tool_node = ToolNode(tools)


# Define the node that calls the model
def call_model(
    state: AgentState,
    config: RunnableConfig,
):
    """
    Invokes the agent model to generate a response based on the current state.

    Args:
        state (messages): The current state

    Returns:
        dict: The updated state with the agent response appended to messages
    """
    system_prompt = SystemMessage(
        f"Date: {date.today().strftime('%A, %Y-%m-%d')}"
        "You are a professional and friendly virtual assistant "
        "for a hair and beauty salon. Your job is to assist customers "
        "with scheduling, rescheduling, and canceling appointments, as "
        "well as providing information about the services offered, the "
        "salon's hours, and the team members. Always provide clear and "
        "concise responses. Be polite, accommodating, and ensure customers "
        "feel valued.\n"
        "If the client want to schedule an appointment you must get the client "
        "data in this order:\n"
        "1. The service.\n"
        "2. The date.\n"
        "3. The team member the client would like.",
    )

    human_prompt = HumanMessage(
        (
            f"The customer ID is {state['customer_id']}.\n"
            "You are not allowed to output any database IDs.\n"
        ),
    )

    response = model.invoke([system_prompt, human_prompt] + state["messages"], config)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define the conditional edge that determines whether to continue or not
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we finish
    if not last_message.tool_calls:
        return "end"
    # Otherwise if there is, we continue
    else:
        return "continue"


### Graph ###

# Define a new graph
workflow = StateGraph(AgentState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    # Finally we pass in a mapping.
    # The keys are strings, and the values are other nodes.
    {
        # If `tools`, then we call the tool node.
        "continue": "tools",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("tools", "agent")

# Now we can compile and visualize our graph
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "1"}}
    inputs = {
        "messages": [
            (
                "user",
                (
                    "I would like to schedule an appointment with Juan on January "
                    "20th morning for a hair cut."
                ),
            ),
        ],
    }
    print_stream(graph.stream(inputs, stream_mode="values", config=config))
    inputs = {
        "messages": [
            (
                "user",
                ("Ok, I want to schedule it at 9:00AM"),
            ),
        ],
    }
    print_stream(graph.stream(inputs, stream_mode="values", config=config))
