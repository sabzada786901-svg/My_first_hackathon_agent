import os
import asyncio
from app.models import KisanDostResponse
from app.agents_config import kisan_dost_agent
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

from app.models import KisanDostResponse


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv()

set_tracing_disabled(True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
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
# MODEL
# =========================================================

model = OpenAIChatCompletionsModel(
    model="openrouter/free",
    openai_client=client,
)


# =========================================================
# 1. INPUT GUARDRAIL
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
        "subsidy",
        "loan",
        "agri",
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

    allowed = (
        any(word in text for word in agriculture_keywords)
        or any(word in text for word in greetings)
    )

    if allowed:
        return GuardrailFunctionOutput(
            output_info="Input is relevant to Kisan Dost.",
            tripwire_triggered=False,
        )

    return GuardrailFunctionOutput(
        output_info="Input is outside agricultural scope.",
        tripwire_triggered=True,
    )


# =========================================================
# 2. PESTICIDE SAFETY GUARDRAIL
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
            output_info="Dangerous pesticide or poisoning request detected.",
            tripwire_triggered=True,
        )

    return GuardrailFunctionOutput(
        output_info="Pesticide safety check passed.",
        tripwire_triggered=False,
    )


# =========================================================
# 3. OUTPUT VALIDATION
# =========================================================

@output_guardrail
async def output_validation_guardrail(
    context,
    agent,
    output,
) -> GuardrailFunctionOutput:

    text = str(output)

    # Empty response check
    if not text.strip():
        return GuardrailFunctionOutput(
            output_info="Empty response detected.",
            tripwire_triggered=True,
        )

    # Extremely long response protection
    if len(text) > 12000:
        return GuardrailFunctionOutput(
            output_info="Response is excessively long.",
            tripwire_triggered=True,
        )

    # Unsafe medical advice
    unsafe_medical_patterns = [
        "take this medicine",
        "take this tablet",
        "medical prescription",
        "human dosage",
        "medicine dosage",
        "you have this disease",
    ]

    # Dangerous pesticide advice
    unsafe_pesticide_patterns = [
        "drink pesticide",
        "pesticide ingestion",
        "pesticide for humans",
        "human pesticide dose",
    ]

    medical_violation = any(
        pattern in text.lower()
        for pattern in unsafe_medical_patterns
    )

    pesticide_violation = any(
        pattern in text.lower()
        for pattern in unsafe_pesticide_patterns
    )

    if medical_violation or pesticide_violation:
        return GuardrailFunctionOutput(
            output_info="Unsafe output detected.",
            tripwire_triggered=True,
        )

    return GuardrailFunctionOutput(
        output_info="Output passed validation.",
        tripwire_triggered=False,
    )


# =========================================================
# 4. KISAN DOST AGENT
# =========================================================

kisan_dost_agent = Agent(
    name="Kisan Dost",

    instructions="""
You are Kisan Dost, an AI agricultural advisor
for Pakistani farmers.

Answer in simple Urdu-English / Roman Urdu.

You help with:

- crop selection
- fertilizer planning
- profit estimation
- mandi prices
- pest and disease diagnosis
- weather and irrigation
- agriculture-related government support

IMPORTANT RULES:

1. Stay focused on agriculture.

2. For crop selection use crop_advisor.

3. crop_advisor requires:
   district
   soil_type
   season
   water_availability
   land_size_acres

4. Never invent missing information.

5. Ask the farmer for missing information.

6. For fertilizer questions use fertilizer_calculator.

7. fertilizer_calculator requires:
   crop
   acres

8. For profit questions use profit_estimator.

9. Never invent tool results.

10. Clearly identify estimated information.

11. Never provide human medical advice.

12. Never recommend pesticide ingestion.

13. Never provide dangerous pesticide instructions.

14. For agricultural pesticide questions,
give safe and general guidance.

15. If the farmer asks something unrelated
to agriculture, politely explain your scope.

16. Be concise, helpful and conversational.

17. Do not claim live data unless a connected
tool actually provides it.

18. If a calculation is performed, explain
the important numbers clearly.
""",

    model=model,

    # =====================================================
    # TOOLS
    # =====================================================

    tools=[
        crop_advisor,
        fertilizer_calculator,
        profit_estimator,
    ],

    # =====================================================
    # GUARDRAILS
    # =====================================================

    input_guardrails=[
        agriculture_input_guardrail,
        pesticide_safety_guardrail,
    ],

    output_guardrails=[
        output_validation_guardrail,
    ],

    # =====================================================
    # 4. PYDANTIC OUTPUT SCHEMA
    # =====================================================

    output_type=KisanDostResponse,
)


# =========================================================
# 5. MAIN CHAT LOOP + ERROR HANDLING
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

        except KeyboardInterrupt:

            print("\n\n🤖 Kisan Dost: Allah Hafiz! 👋🌾")
            break

        except EOFError:

            print("\n\n🤖 Kisan Dost: Allah Hafiz! 👋🌾")
            break

        # =================================================
        # EXIT
        # =================================================

        if question.lower() == "exit":

            print("\n🤖 Kisan Dost: Allah Hafiz! 👋🌾")
            break

        # =================================================
        # EMPTY INPUT
        # =================================================

        if not question:

            print(
                "\n🤖 Kisan Dost: "
                "Please apna question likhein."
            )

            continue

        # =================================================
        # RUN AGENT
        # =================================================

        try:

            result = await Runner.run(
                kisan_dost_agent,
                question,
            )

            print("\n🤖 Kisan Dost:")
            print("-" * 60)

            # Pydantic validated output
            final_output = result.final_output

            if isinstance(
                final_output,
                KisanDostResponse
            ):

                print(final_output.answer)

                if final_output.safety_note:
                    print(
                        f"\n⚠️ {final_output.safety_note}"
                    )

            else:

                print(final_output)

        # =================================================
        # INPUT GUARDRAIL
        # =================================================

        except InputGuardrailTripwireTriggered:

            print(
                "\n🛡️ Kisan Dost:"
                "\nMaaf kijiye, main sirf farming aur "
                "agriculture-related questions mein "
                "madad kar sakta hoon. 🌾"
            )

        # =================================================
        # OUTPUT GUARDRAIL
        # =================================================

        except OutputGuardrailTripwireTriggered:

            print(
                "\n🛡️ Kisan Dost:"
                "\nResponse safety check pass nahi kar saka."
            )

            print(
                "Main safe agricultural guidance "
                "provide kar sakta hoon. 🌾"
            )

        # =================================================
        # GENERAL ERROR
        # =================================================

        except Exception as e:

            print(
                "\n❌ Kisan Dost mein temporary error aa gaya."
            )

            print(
                "Please dobara try karein."
            )

            print(
                f"\nTechnical error: {type(e).__name__}"
            )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    asyncio.run(main())
