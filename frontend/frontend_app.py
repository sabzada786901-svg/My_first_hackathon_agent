import sys
import os
import asyncio

# ==========================================
# PROJECT ROOT
# ==========================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ==========================================
# IMPORTS
# ==========================================

import streamlit as st
from agents import Runner

from kisan_dost_agent import kisan_dost_agent


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="Kisan Dost",
    page_icon="🌾",
    layout="centered"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #000000;
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 0px;
}

.subtitle {
    text-align: center;
    color: #f6f5f6;
    font-size: 17px;
    margin-bottom: 30px;
}

div[data-testid="stChatMessage"] {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="main-title">🌾 Kisan Dost</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI Farmer Assistant for Pakistani Farmers</div>',
    unsafe_allow_html=True
)


# ==========================================
# SESSION MEMORY
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.header("🌾 Kisan Dost")

    st.write(
        "Ask your farming questions in Urdu, "
        "Roman Urdu or English."
    )

    st.divider()

    st.subheader("💡 Try asking")

    st.write("🌱 What should I grow in Rabi?")
    st.write("🧪 How much fertilizer for wheat?")
    st.write("💰 Calculate my crop profit.")
    st.write("🐛 My cotton leaves have white insects.")
    st.write("💧 When should I irrigate?")

    st.divider()

    if st.button("🗑️ Clear Chat", use_container_width=True):

        st.session_state.messages = []

        st.rerun()


# ==========================================
# DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ==========================================
# USER INPUT
# ==========================================

user_input = st.chat_input(
    "👨‍🌾 Apna farming question likhein..."
)


# ==========================================
# AGENT
# ==========================================

if user_input:

    # --------------------------------------
    # Save user message
    # --------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # --------------------------------------
    # Show user message
    # --------------------------------------

    with st.chat_message("user"):
        st.markdown(user_input)

    # --------------------------------------
    # Build conversation history
    # --------------------------------------

    conversation = []

    for message in st.session_state.messages:

        conversation.append({
            "role": message["role"],
            "content": message["content"]
        })

    # --------------------------------------
    # Run agent
    # --------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("🌾 Kisan Dost soch raha hai..."):

            try:

                result = asyncio.run(
                    Runner.run(
                        kisan_dost_agent,
                        conversation
                    )
                )

                response = result.final_output

                # --------------------------------------
                # Handle normal text response
                # --------------------------------------

                if hasattr(response, "answer"):

                    answer = response.answer

                    if hasattr(response, "safety_note"):

                        if response.safety_note:

                            answer += (
                                "\n\n⚠️ **Safety Note:** "
                                + response.safety_note
                            )

                else:

                    answer = str(response)

                # --------------------------------------
                # Display response
                # --------------------------------------

                st.markdown(answer)

                # --------------------------------------
                # Save assistant response
                # --------------------------------------

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })

            except Exception as e:

                error = (
                    "❌ Kisan Dost ko response generate karne "
                    "mein problem hui.\n\n"
                    f"`{str(e)}`"
                )

                st.error(error)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error
                })