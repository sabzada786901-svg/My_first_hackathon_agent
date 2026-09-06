import os

import asyncio


from dotenv import load_dotenv

from agents import (
    Agent,
    Runner,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    set_tracing_disabled,
    input_guardrail,
    output_guardrail,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
)

from app.tools import (
    crop_advisor,
    fertilizer_calculator,
    profit_estimator,
)


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

set_tracing_disabled(True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not groq_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY is missing from .env file"
    )


# =========================================================
# OPENROUTER CLIENT
# =========================================================

client = AsyncOpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)


# =========================================================
# FREE MODEL
# =========================================================

model = OpenAIChatCompletionsModel(
    model="openrouter/free",
    openai_client=client,
)


# =========================================================
# AGRICULTURE INPUT GUARDRAIL
# =========================================================

@input_guardrail
async def agriculture_input_guardrail(
    context,
    agent,
    input,
) -> GuardrailFunctionOutput:
    

    text = str(input).lower().strip()



    agriculture_keywords = [

        "crop",
        "fasal",
        "farmer",
        "kisan",
        "farming",
        "agriculture",
        "agri",
        "zameen",
        "land",
        "soil",
        "mitti",

        "wheat",
        "gandum",
        "cotton",
        "kapas",
        "rice",
        "chawal",
        "maize",
        "makai",
        "chickpea",
        "chana",
        "lentil",
        "masoor",

        "fertilizer",
        "khaad",
        "urea",
        "dap",


        "pesticide",

        "spray",
        "keera",

        "pest",

        "disease",
        "bimari",

        "weather",
        "mausam",
        "rain",
        "barish",
        "irrigation",
        "pani",
        "water",


        "mandi",
        "price",
        "rate",


        "profit",
        "munafa",
        "yield",
        "paidawar",
        "cost",
        "income",

        "subsidy",
        "loan",
        "government",
        "scheme",

        "support",

        "district",
        "acre",
        "acres",
        "season",
        "rabi",
        "kharif",
        "loamy",
    ]

    greetings = [
        "hello",
        "hi",
        "salam",
        "assalam",
        "aoa",
        "help",
        "madad",
    ]


    agriculture_match = any(
        keyword in text
        for keyword in agriculture_keywords
    )

    greeting_match = any(
        greeting in text
        for greeting in greetings
    )

    if agriculture_match or greeting_match:
        return GuardrailFunctionOutput(
            output_info="Agriculture input accepted.",
            tripwire_triggered=False,
        )

    return GuardrailFunctionOutput(
        output_info="Input is outside agriculture scope.",
        tripwire_triggered=True,
    )


# =========================================================
# PESTICIDE SAFETY GUARDRAIL
# =========================================================

@input_guardrail
async def pesticide_safety_guardrail(
    context,
    agent,
    input,
) -> GuardrailFunctionOutput:

    text = str(input).lower()

    dangerous_patterns = [
        "pesticide peena",
        "pesticide peelo",
        "pesticide drink",
        "pesticide khana",
        "pesticide kha lo",
        "human pesticide dose",
        "insaan ko pesticide",
        "person pesticide",
        "pesticide for human",
        "chemical drink",
        "poison drink",
        "zehar peena",
        "zehar kha",
        "suicide pesticide",
    ]

    dangerous_request = any(
        pattern in text
        for pattern in dangerous_patterns
    )

    if dangerous_request:

        return GuardrailFunctionOutput(
            output_info="Dangerous pesticide request detected.",
            tripwire_triggered=True,
        )

    return GuardrailFunctionOutput(
        output_info="Pesticide safety check passed.",
        tripwire_triggered=False,
    )


# =========================================================
# OUTPUT VALIDATION GUARDRAIL
# =========================================================

@output_guardrail
async def output_validation_guardrail(
    context,
    agent,
    output,
) -> GuardrailFunctionOutput:

    text = str(output)


    if not text.strip():

        return GuardrailFunctionOutput(
            output_info="Empty response detected.",
            tripwire_triggered=True,
        )


    if len(text) > 12000:

        return GuardrailFunctionOutput(
            output_info="Response is excessively long.",
            tripwire_triggered=True,
        )

    unsafe_patterns = [
        "take this medicine",
        "take this tablet",
        "medical prescription",
        "human dosage",
        "medicine dosage",
        "you have this disease",

        "drink pesticide",
        "pesticide ingestion",
        "pesticide for humans",
        "human pesticide dose",
    ]

    lower_text = text.lower()

    unsafe = any(
        pattern in lower_text
        for pattern in unsafe_patterns
    )

    if unsafe:
        return GuardrailFunctionOutput(
            output_info="Unsafe output detected.",
            tripwire_triggered=True,
        )

    return GuardrailFunctionOutput(
        output_info="Output passed validation.",
        tripwire_triggered=False,
    )


# =========================================================
# KISAN DOST AGENT
# =========================================================

kisan_dost_agent = Agent(

    name="Kisan Dost",
    model=model,
    instructions="""
You are Kisan Dost, an AI agricultural advisor
for Pakistani farmers.

Answer in simple Roman Urdu / Urdu-English.

You help farmers with:

- crop selection
- fertilizer
- profit estimation
- mandi prices
- pest and disease
- weather
- irrigation
- agriculture support

IMPORTANT RULES:

1. Stay focused on agriculture.
2. When the farmer asks which crop to grow, use crop_advisor.
3. crop_advisor requires: district, soil_type, season, water_availability, land_size_acres.
4. Never invent missing information.
5. If information is missing, ask the farmer.
6. When the farmer asks about fertilizer, use fertilizer_calculator.
7. fertilizer_calculator requires: crop, acres.
8. When the farmer asks about profit, use profit_estimator.
9. Never invent tool results.
10. After using a tool, explain the result naturally to the farmer.
11. NEVER tell the farmer: "I will now call crop_advisor."
12. NEVER mention internal tool names in the final answer.
13. NEVER expose JSON or internal tool data to the farmer.
14. Do not provide human medical advice.
15. Do not provide dangerous pesticide instructions.
16. Keep answers concise and useful.
17. If the question is unrelated to agriculture, politely explain that you are an agriculture assistant.
18. Do not claim live information unless a tool actually provides it.
19. Clearly identify estimates.
""",
    tools=[
        crop_advisor,
        fertilizer_calculator,
        profit_estimator,
    ],

    input_guardrails=[
        agriculture_input_guardrail,
        pesticide_safety_guardrail,
    ],

    output_guardrails=[
        output_validation_guardrail,
    ],

)


# =========================================================
# MAIN CHAT
# =========================================================

async def main():

    print()

    print("=" * 60)
    print("🌾 KISAN DOST — FARMER'S FRIEND")
    print("=" * 60)

    print()
    print("👨‍🌾 Kisan Dost se baat karein.")
    print("💡 Program band karne ke liye 'exit' likhein.")
    print("-" * 60)
    while True:
        try:
            question = input("\n👨‍🌾 Farmer: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n🤖 Kisan Dost: Allah Hafiz! 👋🌾")
            break

        if question.lower() == "exit":
            print("\n🤖 Kisan Dost: Allah Hafiz! 👋🌾")
            break

        if not question:

            print("\n🤖 Kisan Dost: Please apna question likhein.")
            continue

        try:

            result = await Runner.run(
                kisan_dost_agent,
                question,
            )

            print()
            print("🤖 Kisan Dost:")
            print("-" * 60)

            final_output = result.final_output
            print(final_output)

        except InputGuardrailTripwireTriggered:
            print("\n🛡️ Kisan Dost:")
            print(
                "Maaf kijiye, main sirf farming aur "
                "agriculture-related questions mein "
                "madad kar sakta hoon. 🌾"
            )

        except OutputGuardrailTripwireTriggered:
            print("\n🛡️ Kisan Dost:")
            print("Response safety check pass nahi kar saka.")
            print("Main safe agricultural guidance provide kar sakta hoon. 🌾")

        except Exception as e:
            print("\n❌ Kisan Dost mein error aa gaya.")
            print(f"Technical error: {type(e).__name__}")
            print(f"Details: {str(e)}")


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    
    asyncio.run(main())