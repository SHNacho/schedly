import random

import streamlit as st
from llm.agent import graph
from llm.utils import print_stream

st.set_page_config(page_title="Schedly", layout="centered", page_icon="🤖")

# @st.cache_data
# def get_graph():
#    """
#    Function to cache the graph.
#    Avoid generating the graph each iteration.
#    """
#    from llm.agent import graph
#    return graph

# Set up session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        ("bot", "Hi! I'm the beauty salon assitant, how can I help you?"),
    ]
if "thread" not in st.session_state:
    st.session_state.thread = random.randint(1, 4999999)
    print("New user with thread ", st.session_state.thread)

# Mapping ChatBot avatars
avatars = {"user": "user", "bot": "assistant"}


# Display previous messages
for role, content in st.session_state.messages:
    st.chat_message(avatars[role]).write(content)

# Input box for user query
if user_input := st.chat_input("Ask anything:"):

    st.session_state.messages.append(("user", user_input))
    st.chat_message("user").write(user_input)

    inputs = {"messages": [("user", user_input)], "customer_id": 1}
    config = {"configurable": {"thread_id": st.session_state.thread}}

    output = graph.invoke(inputs, stream_mode="values", config=config)
    print_stream(output)
    output_message = output["messages"][-1]
    st.session_state.messages.append(("bot", output_message.content))
    st.chat_message("assistant").write(output_message.content)
