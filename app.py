"""
Streamlit web UI for Cal.com chatbot

This is the USER INTERFACE for the chatbot - a web page where users can chat
with the bot to book, view, cancel, and reschedule meetings.

WHAT IS STREAMLIT?
!Streamlit is a Python framework for building web apps quickly. Instead of writing
!HTML/CSS/JavaScript, you write Python code and Streamlit renders it as a web page.

WHY STREAMLIT?
- Fast to build: Create a web UI in minutes
- Pure Python: No need to learn web technologies
- Interactive: Automatically updates when users interact
- Beautiful: Good-looking UI out of the box

HOW TO RUN:
From terminal: streamlit run app.py
Then open browser to: http://localhost:8501

KEY STREAMLIT CONCEPTS:
- st.chat_message(): Creates chat bubble UI
- st.session_state: Stores data across page reruns (like conversation history)
- st.rerun(): Refreshes the page to show updated content
- asyncio.run(): Runs async functions (needed for our chatbot)
"""

# Import Streamlit and supporting libraries
import streamlit as st  # The Streamlit framework
import asyncio  # For running async functions
from datetime import datetime  # For date/time operations
import os  # For reading environment variables
from dotenv import load_dotenv  # Load .env file

# Import our chatbot
from src.chatbot import CalChatbot

# Load environment variables (API keys, user email, etc.)
load_dotenv()

# Page config - sets browser tab title, icon, and layout
# This MUST be the first Streamlit command
st.set_page_config(
    page_title="Cal.com Meeting Assistant",  # Shows in browser tab
    page_icon="📅",  # Icon in browser tab
    layout="wide",  # Use full width of browser
)

# Custom CSS for styling the page
#! Streamlit allows injecting custom CSS to make the UI look nicer
# The unsafe_allow_html=True flag is needed to render HTML/CSS
st.markdown(
    """
<style>
    /* Main header styling - the big title at top */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;  /* Blue color */
        margin-bottom: 0.5rem;
    }
    /* Subtitle styling */
    .sub-header {
        font-size: 1rem;
        color: #666;  /* Gray color */
        margin-bottom: 2rem;
    }
    /* General chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;  /* Rounded corners */
        margin-bottom: 1rem;
    }
    /* User messages - light blue background */
    .user-message {
        background-color: #e3f2fd;
    }
    /* Assistant messages - light gray background */
    .assistant-message {
        background-color: #f5f5f5;
    }
    /* Sidebar info boxes - yellow background */
    .sidebar-info {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state
#! SESSION STATE is how Streamlit stores data across page reruns
#! Every time user interacts, Streamlit reruns the entire script
#! Session state persists data between these reruns

# Store conversation messages
# This is a list of {"role": "user/assistant", "content": "message text"}
if "messages" not in st.session_state:
    st.session_state.messages = []

# Store chatbot instance
#! We create this once and reuse it (expensive to recreate)
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None

# Store user's email
# Try to load from environment, otherwise empty string
if "user_email" not in st.session_state:
    st.session_state.user_email = os.getenv("CAL_USER_EMAIL", "")


async def init_chatbot():
    """
    Initialize the chatbot (create it if it doesn't exist)

    WHY ASYNC?
    Our chatbot's methods are async (they use await), so we need to
    call them from an async function.

    WHY CHECK IF NONE?
    We only want to create the chatbot once (it's expensive).
    After first creation, we reuse the same instance.
    """
    if st.session_state.chatbot is None:
        st.session_state.chatbot = CalChatbot()


async def send_message(user_message: str, user_email: str):
    """
    Send a message to the chatbot and get a response

    This is a wrapper around chatbot.chat() that's called from the UI.
    It handles the async call and returns the response.

    Args:
        user_message: The user's new message
        user_email: The user's email (needed for booking operations)

    Returns:
        Tuple of (response text, updated conversation history)
    """
    # Call the chatbot with current message and conversation history
    response, updated_history = await st.session_state.chatbot.chat(
        user_message=user_message,
        conversation_history=st.session_state.messages,
        user_email=user_email,
    )
    return response, updated_history


# ============================================================================
# MAIN UI LAYOUT
# ============================================================================

# Display the main header and subtitle
# Using custom CSS classes defined above for styling
st.markdown(
    '<div class="main-header">📅 Cal.com Meeting Assistant</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-header">Book, view, and manage your meetings with natural language</div>',
    unsafe_allow_html=True,
)

# ============================================================================
# SIDEBAR - Settings and instructions
# ============================================================================
# The sidebar shows on the left side of the page
# It contains settings, instructions, and actions
with st.sidebar:
    st.header("⚙️ Settings")

    # User email input field
    # This is crucial for booking and listing meetings
    user_email = st.text_input(
        "Your Email",
        value=st.session_state.user_email,  # Pre-fill with stored value
        help="Your email address for booking queries",  # Hover tooltip
    )
    # Save the email back to session state
    st.session_state.user_email = user_email

    # Horizontal divider
    st.markdown("---")

    # Instructions section - what the chatbot can do
    st.markdown("### 💡 What I can do:")
    st.markdown(
        """
    - **Book meetings**: "Help me book a meeting"
    - **List meetings**: "Show me my scheduled events"
    - **Cancel meetings**: "Cancel my 3pm meeting today"
    - **Reschedule meetings**: "Move my meeting to tomorrow"
    """
    )

    st.markdown("---")

    # Tips section - how to use the chatbot effectively
    st.markdown("### 📝 Tips:")
    st.markdown(
        """
    - Use natural language for dates/times
    - Provide your email for booking queries
    - Be specific when canceling/rescheduling
    """
    )

    st.markdown("---")

    # Clear chat button - resets the conversation
    # use_container_width makes button fill the sidebar width
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []  # Clear message history
        st.rerun()  # Refresh the page to show empty chat

    # Status indicator - shows if chatbot is ready
    if st.session_state.chatbot:
        st.success("✅ Chatbot Ready")  # Green success box
    else:
        st.info("🔄 Initializing...")  # Blue info box

# ============================================================================
# INITIALIZE CHATBOT
# ============================================================================
# Create the chatbot instance if it doesn't exist yet
# asyncio.run() is needed because init_chatbot is async
asyncio.run(init_chatbot())

# ============================================================================
# CHAT INTERFACE - Display conversation history
# ============================================================================
# Create a container for the chat messages
chat_container = st.container()

with chat_container:
    # Display all previous messages in the conversation
    # Loop through each message in session state
    for msg in st.session_state.messages:
        role = msg["role"]  # "user" or "assistant"
        content = msg["content"]  # The message text

        # Display user messages
        if role == "user":
            # st.chat_message() creates a chat bubble with avatar
            with st.chat_message("user"):
                st.markdown(content)  # Display the text

        # Display assistant (chatbot) messages
        elif role == "assistant":
            with st.chat_message("assistant"):
                st.markdown(content)

# ============================================================================
# CHAT INPUT - Handle new user messages
# ============================================================================
# st.chat_input() creates the text input box at bottom of page
#! The ":=" operator assigns the value AND checks if it's truthy
# So this runs only when user submits a message
if prompt := st.chat_input("Type your message here..."):
    # VALIDATION: Check if email is needed but missing
    # Some operations (like listing meetings) require an email
    # Check if user is asking to see meetings without providing email
    if not st.session_state.user_email and any(
        keyword in prompt.lower()
        for keyword in ["show", "list", "my meetings", "my events"]
    ):
        st.error("⚠️ Please provide your email in the sidebar to view your meetings")
    else:
        # Add user message to conversation history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display the user's message immediately
        # This gives instant feedback while bot is thinking
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display bot response
        with st.chat_message("assistant"):
            # Show spinner while waiting for response
            # This tells user the bot is processing (can take a few seconds)
            with st.spinner("Thinking..."):
                try:
                    # Call the chatbot to get response
                    # asyncio.run() executes the async function
                    response, updated_history = asyncio.run(
                        send_message(prompt, st.session_state.user_email)
                    )

                    # Update session state with new conversation history
                    # This includes both the user message and bot response
                    st.session_state.messages = updated_history

                    # Display the bot's response
                    st.markdown(response)

                except Exception as e:
                    # If anything goes wrong, show error message
                    # This catches errors from OpenAI API, Cal.com API, etc.
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)  # Display red error box
                    # Add error to conversation history so it persists
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")  # Horizontal divider
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9rem;">'
    "Powered by OpenAI GPT-4 and Cal.com API"
    "</div>",
    unsafe_allow_html=True,
)
