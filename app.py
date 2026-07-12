import os
import random
from dotenv import load_dotenv
import streamlit as st
from google import genai

# Set up the page before anything else
st.set_page_config(
    page_title="🌌 The Multiverse of Chatbots",
    page_icon="🌌",
    layout="centered"
)

# Load the API key from the .env file or Streamlit secrets
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass

if not api_key:
    st.error("🔑 **GEMINI_API_KEY not found!**")
    st.info("""
    To run this app on Streamlit Cloud, you need to configure your Google Gemini API Key in the Secrets manager:
    1. In the lower right of your Streamlit app, click **Manage app** (or go to your Streamlit dashboard).
    2. Click the three dots icon next to your app and select **Settings**.
    3. Go to **Secrets** and paste the following:
    ```toml
    GEMINI_API_KEY = "your_actual_api_key_here"
    ```
    4. Click **Save** and wait for the app to restart.
    """)
    st.stop()

# Create the Gemini client
client = genai.Client(api_key=api_key)

# Task 1: Initialize the Memory Vault
# HOW IT WORKS: It checks if the "messages" list is already stored in Streamlit's st.session_state.
# If it is not present (e.g. first-time load), it initializes st.session_state.messages as an empty list [].
# WHERE IT EXECUTES: It runs right at the start of the app execution (below the Gemini client initialization),
# ensuring that the state exists before any other UI rendering or database writes happen.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_log" not in st.session_state:
    st.session_state.conversation_log = []

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Chat Settings")

    # Let the user choose who they want to chat with
    personality = st.selectbox(
        "Choose a Character",
        [
            "🛡 Captain America",
            "🧛 A Pookie Vampire",
            "🏏 Angry Ravi Shastri",
            "🤖 Jarvis",
            "⚡ Iron Man",
            "🕷 Spider-Man",
            "🃏 Joker",
            "🦇 Batman",
            "🧙 Harry Potter",
            "🧠 Sherlock Holmes",
            "🐼 Po",
            "🧙 Gandalf"
        ]
    )

    # Short descriptions for every character
    descriptions = {
        "🛡 Captain America": "Brave, disciplined and inspiring leader.",
        "🧛 A Pookie Vampire": "Cute, dramatic and hopeless romantic vampire.",
        "🏏 Angry Ravi Shastri": "Loud, energetic cricket commentator with high intensity.",
        "🤖 Jarvis": "Highly professional, intelligent AI assistant.",
        "⚡ Iron Man": "Sarcastic, witty, billionaire genius philanthropist.",
        "🕷 Spider-Man": "Funny, friendly, talkative neighborhood superhero.",
        "🃏 Joker": "Chaotic, mysterious, insane and highly unpredictable.",
        "🦇 Batman": "Serious, dark, logical protector and detective of Gotham.",
        "🧙 Harry Potter": "Kind-hearted, courageous young wizard.",
        "🧠 Sherlock Holmes": "Master detective utilizing brilliant logical deduction.",
        "🐼 Po": "Funny, enthusiastic kung-fu warrior panda.",
        "🧙 Gandalf": "Wise, deep and powerful guide wizard."
    }

    # Show a short description of the selected character
    st.info(descriptions.get(personality, ""))

    # Let the user decide how detailed the reply should be
    response_length = st.select_slider(
        "Response Length",
        options=["Short", "Medium", "Long"],
        value="Medium"
    )

    st.markdown("---")

    # Clear the conversation and start fresh
    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Extract character name and emoji
emoji = personality.split()[0]
char_name = " ".join(personality.split()[1:])

# Main page headings
st.title("🌌 The Multiverse of Chatbots")
st.write("Step into another dimension and chat with your favorite characters")

# Active Character Card in Main Area
st.subheader(f"{emoji} {char_name}")
st.write(descriptions.get(personality, ""))

# Display a welcome message if the conversation is empty
if len(st.session_state.messages) == 0:
    welcome = random.choice([
        f"🌟 Welcome! Click the input box below to start chatting with {char_name}.",
        f"🚀 Enter the portal and speak with {char_name}!",
        f"🌀 You are now connected to the universe of {char_name}!",
        f"🎭 {char_name} is waiting for you. Say hello!"
    ])
    st.info(welcome)

# Task 2: Render the Chat History
# HOW IT WORKS: It iterates through every dictionary stored in st.session_state.messages and renders 
# them dynamically using st.chat_message() based on their role ("user" or "assistant").
# WHERE IT EXECUTES: This loop executes on every single rerun of the script, drawing all past 
# conversation messages on the main page to prevent state loss/chatbot amnesia.
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar=emoji):
            st.write(message["content"])

# Task 3: Upgrade the Input UI
# HOW IT WORKS: Replaces the deprecated st.text_input and st.button combination with Streamlit's native st.chat_input().
# It uses the Python walrus operator (:=) to assign the input text to the 'user_message' variable and checks if there is active
# text in a single step inside the conditional if statement.
# WHERE IT EXECUTES: Located at the bottom of the script. This block executes dynamically when the user types a message and hits enter.
if user_message := st.chat_input("Say something..."):
    # Display the user's message immediately
    with st.chat_message("user", avatar="👤"):
        st.write(user_message)

    # Task 4: Save New Messages to Memory (User Message)
    # HOW IT WORKS: Appends a dictionary representing the user's input {"role": "user", "content": user_message} to st.session_state.messages.
    # WHERE IT EXECUTES: Runs immediately inside the chat input block as soon as the user enters a new message, updating the memory vault.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )
    st.session_state.conversation_log.append(
        {
            "role": "user",
            "content": user_message
        }
    )

    # Combine all previous messages into one conversation
    conversation = ""
    for msg in st.session_state.messages:
        conversation += f"{msg['role']}: {msg['content']}\n"

    # Tell Gemini how it should behave
    ai_instructions = f"""
You are {personality}.

Rules:
- Stay completely in character.
- Never say you are an AI.
- Talk exactly like {personality}.
- Be engaging and entertaining.
- Use emojis whenever they fit naturally.
- Remember the previous conversation.
- Reply in {response_length.lower()} length.

Conversation:

{conversation}

User:
{user_message}
"""

    with st.chat_message("assistant", avatar=emoji):
        # Show a typing animation while waiting for the reply
        with st.spinner(f"{char_name} is thinking..."):
            try:
                # Ask Gemini to generate a response
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=ai_instructions
                )

                # Store the generated reply
                reply = response.text

                # Display the reply on the screen
                st.write(reply)

                # Task 4: Save New Messages to Memory (Assistant Response)
                # HOW IT WORKS: Appends a dictionary representing the assistant's reply {"role": "assistant", "content": reply} to st.session_state.messages.
                # WHERE IT EXECUTES: Runs after the Gemini API generates and returns a text reply, registering it in the session state history before copy options are displayed.
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reply
                    }
                )
                st.session_state.conversation_log.append(
                    {
                        "role": "assistant",
                        "content": reply,
                        "char_name": char_name,
                        "emoji": emoji
                    }
                )

                # Make it easy to copy the response
                with st.expander("📋 Copy Response"):
                    st.code(reply)

            # Show any errors if something goes wrong
            except Exception as e:
                st.error(f"Error: {e}")

# A simple footer for the app
st.markdown("---")
st.caption("🌌 Made with ❤️ using Streamlit and Gemini 2.5 Flash")

# Render the Conversation Log in the sidebar at the very end of the script
# so it includes any new messages sent in this run.
with st.sidebar:
    st.markdown("---")
    with st.expander("📜 Conversation Log", expanded=True):
        if not st.session_state.conversation_log:
            st.info("Start chatting to see logs here.")
        else:
            i = 0
            n = len(st.session_state.conversation_log)
            while i < n:
                msg = st.session_state.conversation_log[i]
                if msg["role"] == "user":
                    user_content = msg["content"]
                    st.markdown(f"👤 **You**: {user_content}")
                    
                    # Check if the next message is the assistant response to pair them
                    if i + 1 < n and st.session_state.conversation_log[i+1]["role"] == "assistant":
                        assistant_msg = st.session_state.conversation_log[i+1]
                        role_label = assistant_msg.get("char_name", char_name)
                        role_emoji = assistant_msg.get("emoji", emoji)
                        
                        # Show a dropdown (st.expander) containing the AI's reply
                        with st.expander(f"{role_emoji} View {role_label}'s Response"):
                            st.write(assistant_msg["content"])
                        i += 2
                    else:
                        i += 1
                else:
                    # Fallback for solo assistant messages (e.g. if a user message is missing)
                    role_label = msg.get("char_name", char_name)
                    role_emoji = msg.get("emoji", emoji)
                    with st.expander(f"{role_emoji} View {role_label}'s Response"):
                        st.write(msg["content"])
                    i += 1