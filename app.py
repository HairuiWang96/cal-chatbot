"""
Streamlit web UI for Cal.com chatbot
Run with: streamlit run app.py
"""

import streamlit as st
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

from src.chatbot import CalChatbot

load_dotenv()

# Page config
st.set_page_config(
    page_title="Cal.com Meeting Assistant",
    page_icon="📅",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .sidebar-info {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chatbot" not in st.session_state:
    st.session_state.chatbot = None

if "user_email" not in st.session_state:
    st.session_state.user_email = os.getenv("CAL_USER_EMAIL", "")


async def init_chatbot():
    """Initialize the chatbot"""
    if st.session_state.chatbot is None:
        st.session_state.chatbot = CalChatbot()


async def send_message(user_message: str, user_email: str):
    """Send a message to the chatbot"""
    response, updated_history = await st.session_state.chatbot.chat(
        user_message=user_message,
        conversation_history=st.session_state.messages,
        user_email=user_email
    )
    return response, updated_history


# Main UI
st.markdown('<div class="main-header">📅 Cal.com Meeting Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Book, view, and manage your meetings with natural language</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # User email input
    user_email = st.text_input(
        "Your Email",
        value=st.session_state.user_email,
        help="Your email address for booking queries"
    )
    st.session_state.user_email = user_email

    st.markdown("---")

    st.markdown("### 💡 What I can do:")
    st.markdown("""
    - **Book meetings**: "Help me book a meeting"
    - **List meetings**: "Show me my scheduled events"
    - **Cancel meetings**: "Cancel my 3pm meeting today"
    - **Reschedule meetings**: "Move my meeting to tomorrow"
    """)

    st.markdown("---")

    st.markdown("### 📝 Tips:")
    st.markdown("""
    - Use natural language for dates/times
    - Provide your email for booking queries
    - Be specific when canceling/rescheduling
    """)

    st.markdown("---")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Status indicator
    if st.session_state.chatbot:
        st.success("✅ Chatbot Ready")
    else:
        st.info("🔄 Initializing...")

# Initialize chatbot
asyncio.run(init_chatbot())

# Chat interface
chat_container = st.container()

with chat_container:
    # Display chat history
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]

        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        elif role == "assistant":
            with st.chat_message("assistant"):
                st.markdown(content)

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Check if email is provided for certain queries
    if not st.session_state.user_email and any(keyword in prompt.lower() for keyword in ["show", "list", "my meetings", "my events"]):
        st.error("⚠️ Please provide your email in the sidebar to view your meetings")
    else:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response, updated_history = asyncio.run(
                        send_message(prompt, st.session_state.user_email)
                    )

                    # Update messages
                    st.session_state.messages = updated_history

                    # Display response
                    st.markdown(response)
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
    'Powered by OpenAI GPT-4 and Cal.com API'
    '</div>',
    unsafe_allow_html=True
)
