import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from agent import get_agent
#from langfuse.callback import CallbackHandler

st.set_page_config(page_title="Agent Chat", page_icon="🤖")
st.title("AI Agent Chat")

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

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("What can you help me with?"):
    # Display user message in chat message container
    st.chat_message("user").markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    if agent:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Initialize Langfuse CallbackHandler
                    # It will automatically pick up LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST from env
                    #langfuse_handler = CallbackHandler()

                    # Prepare messages for the agent
                    lc_messages = []
                    for msg in st.session_state.messages:
                        if msg["role"] == "user":
                            lc_messages.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            lc_messages.append(AIMessage(content=msg["content"]))
                    
                    # Invoke the agent with the callback handler
                    # The agent expects a dictionary with "messages"
                    result = agent.invoke(
                        {"messages": lc_messages},
                        #config={"callbacks": [langfuse_handler]}
                    )
                    
                    # Extract the response
                    # Assuming result["messages"][-1] is the AI message as per notebook
                    response_content = result["messages"][-1].content
                    
                    st.markdown(response_content)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response_content})
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    else:
        st.error("Agent is not initialized.")
