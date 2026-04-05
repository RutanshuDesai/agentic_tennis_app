import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent import get_agent
#from langfuse.callback import CallbackHandler


import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting Tennis agentic application")


st.set_page_config(page_title="Agent Chat", page_icon="🤖")
st.title("Personal AI Agent Assistant Chat")

# Setup Agent
@st.cache_resource
def get_cached_agent(use_ollama: bool):
    return get_agent(use_ollama)

try:
    agent = get_cached_agent(use_ollama=True)
except Exception as e:
    st.error(f"Error creating agent: {e}")
    agent = None

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat from session only (single source of truth — avoids duplicate + grey "stale" bubbles)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Persist new user input, then rerun (do not also render user via a second chat_message in this run)
if prompt := st.chat_input("What can you help me with?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()

# When the last message is from the user, generate the assistant reply on the next run
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    if agent:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    lc_messages = []
                    for msg in st.session_state.messages:
                        if msg["role"] == "user":
                            lc_messages.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            lc_messages.append(AIMessage(content=msg["content"]))

                    result = agent.invoke(
                        {"messages": lc_messages},
                    )
                    response_content = result["messages"][-1].content
                    st.markdown(response_content)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": response_content}
                    )
                    st.rerun()
                except Exception as e:
                    err = f"An error occurred: {e}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})
                    st.rerun()
    else:
        with st.chat_message("assistant"):
            st.error("Agent is not initialized.")
        st.session_state.messages.append(
            {"role": "assistant", "content": "Agent is not initialized."}
        )
        st.rerun()
