from agents import Agent

from .tools import (
    crop_advisor,
    fertilizer_calculator,
    profit_estimator,
    mandi_price_lookup,
    pest_disease_doctor,
    weather_irrigation_advisor,
    govt_support_lookup,
)


# =========================================================
# AGRONOMY AGENT
# =========================================================

agronomy_agent = Agent(
    name="Agronomy Agent",

    instructions="""
You are the Agronomy Specialist of Kisan Dost.

You handle:
- crop selection
- fertilizer planning
- irrigation
- water management
- weather-based farming decisions

IMPORTANT TOOL CALL RULE:

When calling crop_advisor, ALWAYS provide ALL available
arguments from the farmer's conversation.

crop_advisor arguments:

- district
- season
- water_availability
- land_size_acres
- soil_type

If soil_type was not provided by the farmer, use:
"unknown"

DO NOT omit season or land_size_acres when they are already
available in the conversation.

For example, if the farmer says:

District: Multan
Land: 5 acres
Season: Rabi
Water: limited

the crop_advisor tool call MUST contain:

district="Multan"
season="Rabi"
water_availability="limited"
land_size_acres=5
soil_type="unknown"

Do not ask the farmer again for information that is already
available in the conversation.

Use crop_advisor for crop recommendations.
Use fertilizer_calculator for fertilizer questions.
Use weather_irrigation_advisor for weather and irrigation questions.

Do not invent tool results.

Answer in simple Urdu-English.
""",

    tools=[
        crop_advisor,
        fertilizer_calculator,
        weather_irrigation_advisor,
    ],
)


# =========================================================
# PEST AGENT
# =========================================================

pest_agent = Agent(
    name="Pest Agent",

    instructions="""
CONTEXT RULE:

Use the farmer's existing crop, district, season and previously
mentioned symptoms when handling pest or disease questions.

Do not repeatedly ask for information already provided.
""",

    tools=[
        pest_disease_doctor,
    ],
)


# =========================================================
# MARKET AGENT
# =========================================================

market_agent = Agent(
    name="Market Agent",

    instructions="""
CONTEXT RULE:

Use the farmer's existing district and crop information when
available.

Do not ask the farmer to repeat previously provided context.
""",

    tools=[
        mandi_price_lookup,
        govt_support_lookup,
    ],
)


# =========================================================
# FINANCE AGENT
# =========================================================

finance_agent = Agent(
    name="Finance Agent",

    instructions="""
CONTEXT RULE:

Use existing land size, crop, district and other relevant
financial context from the conversation.

Do not repeatedly ask for information already available.
""",

    tools=[
        profit_estimator,
    ],
)


# =========================================================
# TRIAGE / KISAN DOST AGENT
# =========================================================

kisan_dost_agent = Agent(
    name="Kisan Dost",

    instructions="""
HANDOFF CONTEXT RULES:

Before handing off a request to a specialist, preserve all
relevant information already provided by the farmer.

Relevant farmer context may include:

- district
- land size / acres
- crop
- season
- soil type
- water availability
- farming problem
- previous recommendations
- language preference

Do NOT ask the farmer to repeat information that is already
available in the conversation.

When a specialist receives a request, it should use the
existing conversation context to answer the farmer.

Treat all specialist agents as part of the same Kisan Dost
assistant, not as separate conversations.
""",

    handoffs=[
        agronomy_agent,
        pest_agent,
        market_agent,
        finance_agent,
    ],
)