import sys
import os
import asyncio

import streamlit as st
from agents import Runner


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from kisan_dost_agent import kisan_dost_agent


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Kisan Dost | AI Agriculture Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
<style>

/* =========================================
   GLOBAL
========================================= */

.stApp {
    background-color: #F4F7F3 !important;
    color: #17251C !important;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* =========================================
   ALL TEXT
========================================= */

.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp div,
.stApp h1,
.stApp h2,
.stApp h3,
.stApp h4,
.stApp h5,
.stApp h6 {
    color: #17251C;
}


/* =========================================
   HEADINGS
========================================= */

h1 {
    color: #124C2C !important;
    font-size: 42px !important;
    font-weight: 800 !important;
}

h2 {
    color: #176B3A !important;
    font-weight: 800 !important;
}

h3 {
    color: #176B3A !important;
    font-weight: 750 !important;
}


/* =========================================
   CAPTION
========================================= */

.stCaption,
[data-testid="stCaptionContainer"] {
    color: #607268 !important;
}


/* =========================================
   SIDEBAR
========================================= */

section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #D9E5DC;
}

section[data-testid="stSidebar"] * {
    color: #173D29 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #124C2C !important;
}


/* Sidebar buttons */

section[data-testid="stSidebar"] .stButton button {
    background-color: #FFFFFF !important;
    color: #176B3A !important;
    border: 1px solid #D7E4DA !important;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background-color: #176B3A !important;
    color: #FFFFFF !important;
}


/* =========================================
   SUCCESS BOX
========================================= */

div[data-testid="stAlert"] {
    background-color: #E6F4EA !important;
    border: 1px solid #B9DCC2 !important;
}

div[data-testid="stAlert"] * {
    color: #176B3A !important;
}


/* =========================================
   METRIC CARDS
========================================= */

div[data-testid="stMetric"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DCE7DF !important;
    border-radius: 16px !important;
    padding: 18px !important;
    box-shadow: 0 4px 15px rgba(23, 61, 41, 0.06);
}

div[data-testid="stMetric"] * {
    color: #173D29 !important;
}

div[data-testid="stMetricLabel"] {
    color: #176B3A !important;
    font-weight: 700 !important;
}

div[data-testid="stMetricValue"] {
    color: #124C2C !important;
    font-weight: 800 !important;
}

div[data-testid="stMetricDelta"] {
    color: #5C7566 !important;
}


/* =========================================
   CHAT
========================================= */

div[data-testid="stChatMessage"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DCE7DF !important;
    border-radius: 15px !important;
    color: #17251C !important;
}

div[data-testid="stChatMessage"] * {
    color: #17251C !important;
}


/* =========================================
   CHAT INPUT
========================================= */

div[data-testid="stChatInput"] {
    background-color: #FFFFFF !important;
    border: 1px solid #AFCDB8 !important;
    border-radius: 15px !important;
}

div[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
}

div[data-testid="stChatInput"] textarea::placeholder {
    color: #FFFFFF !important;
}


/* =========================================
   BUTTONS
========================================= */

.stButton > button {
    background-color: #FFFFFF !important;
    color: #176B3A !important;

    border: 1px solid #D5E3D9 !important;
    border-radius: 10px !important;

    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: #176B3A !important;
    color: #FFFFFF !important;
    border-color: #176B3A !important;
}


/* =========================================
   DIVIDER
========================================= */

hr {
    border-color: #DCE7DF !important;
}


/* =========================================
   FOOTER
========================================= */

.footer-text {
    color: #6D7E73 !important;
    text-align: center;
    font-size: 12px;
}


/* =========================================
   DARK TOP BAR COMPATIBILITY
========================================= */

header[data-testid="stHeader"] {
    background-color: #ffffff !important;
}

header[data-testid="stHeader"] * {
    color: #FFFFFF !important;
}


/* =========================================
   MOBILE
========================================= */

@media (max-width: 768px) {

    h1 {
        font-size: 32px !important;
    }

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("🌾 Kisan Dost")

    st.caption("AI Agriculture Assistant")

    st.divider()

    st.subheader("👨‍🌾 Farmer Profile")

    st.info(
        "Pakistani Farmer\n\n"
        "🌱 Smart Farming Support"
    )

    st.divider()

    st.subheader("💡 Quick Questions")

    quick_questions = [
        "🌱 What should I grow in Rabi?",
        "🧪 How much fertilizer for wheat?",
        "💰 Calculate my crop profit",
        "🐛 My cotton has white insects",
        "💧 When should I irrigate?"
    ]

    for question in quick_questions:

        if st.button(
            question,
            use_container_width=True
        ):

            st.session_state["quick_question"] = question


    st.divider()

    st.subheader("🟢 System Status")

    st.success(
        "Kisan Dost AI is online"
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        if "quick_question" in st.session_state:
            del st.session_state["quick_question"]

        st.rerun()


# =========================================================
# HERO SECTION
# =========================================================

st.title("🌾 Kisan Dost")

st.subheader(
    "AI-Powered Smart Farming Assistant"
)

st.write(
    "Get intelligent support for crop selection, fertilizer, "
    "profit estimation, pest problems and farming decisions."
)

st.success(
    "🌱 Built to help Pakistani farmers make smarter decisions."
)

st.divider()


# =========================================================
# SMART FARMING TOOLS
# =========================================================

st.subheader("🛠️ Smart Farming Tools")

st.caption(
    "AI-powered agriculture tools for better farming decisions."
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        label="🌱 Crop Advisor",
        value="AI",
        delta="Crop Planning"
    )

    st.caption(
        "Find suitable crops based on your farm conditions."
    )


with col2:

    st.metric(
        label="🧪 Fertilizer",
        value="Smart",
        delta="Nutrient Planning"
    )

    st.caption(
        "Get fertilizer guidance for your selected crop."
    )


with col3:

    st.metric(
        label="💰 Profit Estimator",
        value="Estimate",
        delta="Farm Economics"
    )

    st.caption(
        "Estimate costs, revenue and expected profit."
    )


with col4:

    st.metric(
        label="🐛 Pest Doctor",
        value="Detect",
        delta="Crop Health"
    )

    st.caption(
        "Get help identifying common crop problems."
    )


st.divider()


# =========================================================
# CHAT SECTION
# =========================================================

st.subheader("💬 Ask Kisan Dost")

st.caption(
    "Ask your farming questions in Urdu, Roman Urdu or English."
)


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(
            message["content"]
        )


# =========================================================
# USER INPUT
# =========================================================

user_input = st.chat_input(
    "👨‍🌾 Ask Kisan Dost about your farm..."
)


# =========================================================
# QUICK QUESTION
# =========================================================

if "quick_question" in st.session_state:

    if not user_input:

        user_input = st.session_state["quick_question"]

        del st.session_state["quick_question"]


# =========================================================
# RUN AGENT
# =========================================================

if user_input:

    # Save user message

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })


    # Show user message

    with st.chat_message("user"):

        st.markdown(user_input)


    # Build conversation

    conversation = []

    for message in st.session_state.messages:

        conversation.append({
            "role": message["role"],
            "content": message["content"]
        })


    # AI Response

    with st.chat_message("assistant"):

        with st.spinner(
            "🌾 Kisan Dost aapke sawal ka jawab prepare kar raha hai..."
        ):

            try:

                result = asyncio.run(
                    Runner.run(
                        kisan_dost_agent,
                        conversation
                    )
                )

                response = result.final_output


                # Structured / normal response

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


                # Show answer

                st.markdown(answer)


                # Save answer

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer
                })


            except Exception as e:

                error = (
                    "❌ Kisan Dost ko response generate "
                    "karne mein problem hui.\n\n"
                    f"`{str(e)}`"
                )

                st.error(error)

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error
                })


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🌾 Kisan Dost • AI Agriculture Assistant for Pakistani Farmers"
)

st.caption(
    "Empowering Farmers with AI • Smart Decisions • Better Future"
)