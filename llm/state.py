from collections.abc import Sequence
from typing import Annotated
from typing import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


# Create agent state
class AgentState(TypedDict):
    # The add_messages function defines how an update should be processed
    # Default is to replace. add_messages says "append"
    messages: Annotated[Sequence[BaseMessage], add_messages]
    customer_id: int
