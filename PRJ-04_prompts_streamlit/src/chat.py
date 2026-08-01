import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
from client import SimpleMCPClient

st.set_page_config(
    page_title="Chat MCP",
    page_icon="💬",
    layout="wide"
)

@st.cache_resource
def get_client():
    return SimpleMCPClient()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "context_chat" not in st.session_state:
    st.session_state.context_chat = None
if "first_interaction" not in st.session_state:
    st.session_state.first_interaction = True

st.title("Chat MCP")

chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

if prompt := st.chat_input("Digite sua mensagem..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with chat_container:
        with st.chat_message("user"):
            st.write(prompt)
            
    client = get_client()
    
    if st.session_state.first_interaction:
        response = asyncio.run(client.query_with_prompt(prompt))
        st.session_state.context_chat = response
        st.session_state.first_interaction = False
    else:
        response = asyncio.run(client.continue_chat(prompt, st.session_state.context_chat))
        st.session_state.context_chat = response
        
    assistant_message = response[-1]["content"]
    st.session_state.messages.append({"role": "assistant", "content": assistant_message})
    
    with chat_container:
        with st.chat_message("assistant"):
            st.write(assistant_message)
