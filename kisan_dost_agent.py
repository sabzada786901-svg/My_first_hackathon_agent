import os
import json
import asyncio

from pathlib import Path
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

from app.models import KisanDostResponse

from app.agents_config import (
    agronomy_agent,
    pest_agent,
    market_agent,
    finance_agent,
)


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
# MEMORY SYSTEM
# =========================================================

MEMORY_FILE = Path("memory.json")


def load_memory():
    """Load previous farmer conversation."""

    if not MEMORY_FILE.exists():
        return []

    try:
        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            return []

    except (
        json.JSONDecodeError,
        OSError,
    ):

        return []


def save_memory(memory):
    """Save farmer conversation."""

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                memory,
                file,
                ensure_ascii=False,
                indent=4,
            )

    except OSError as e:

        print(
            f"\n⚠️ Memory save failed: {e}"
        )


def build_context(memory, current_question):
    """
    Build conversation context from previous
    farmer messages and current question.
    """

    context_parts = []

    if memory:

        context_parts.append(
            "PREVIOUS FARMER CONVERSATION:"
        )

        for item in memory:

            farmer_message = item.get(
                "farmer",
                ""
            )

            assistant_message = item.get(
                "assistant",
                ""
            )

            context_parts.append(
                f"Farmer: {farmer_message}"
            )

            context_parts.append(
                f"Kisan Dost: {assistant_message}"
            )

    context_parts.append(
        "CURRENT FARMER QUESTION:"
    )

    context_parts.append(
        current_question
    )

    return "\n\n".join(context_parts)


# =========================================================
# 1. INPUT GUARDRAIL
# =========================================================

@input_guardrail
async def agriculture_input_guardrail(
    context,
    agent,
    input,
) -> GuardrailFunctionOutput:

    return GuardrailFunctionOutput(
        output_info="Input accepted for Kisan Dost.",
        tripwire_triggered=False,
    )

    # Safely convert input to text
    if isinstance(input, str):

        text = input.lower().strip()

    else:

        text = str(input).lower().strip()

    # Agriculture keywords
    agriculture_keywords = [

        # General
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

        # Crops
        "wheat",
        "gandum",
        "cotton",
        "kapas",
        "rice",
        "chawal",
        "maize",
        "makai",
        "chana",
        "masoor",

        # Fertilizer
        "fertilizer",
        "khaad",
        "urea",
        "dap",

        # Pest
        "pesticide",
        "spray",
        "keera",
        "keeray",
        "pest",
        "disease",
        "bimari",

        # Weather
        "weather",
        "mausam",
        "rain",
        "barish",
        "irrigation",
        "pani",
        "water",

        # Market
        "mandi",
        "price",
        "rate",
        "market",

        # Finance
        "profit",
        "munafa",
        "yield",
        "paidawar",
        "cost",
        "income",

        # Government
        "subsidy",
        "loan",
        "government",
        "scheme",
        "program",
        "support",

        # Farmer information
        "district",
        "acre",
        "acres",
        "season",
        "rabi",
        "kharif",
        "soil type",
        "water availability",
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

    # Memory-based follow-up questions
    follow_up_questions = [

        "batao",
        "ab batao",
        "phir batao",
        "aur batao",
        "mujhe batao",

        "kya ugau",
        "kya ugaon",
        "kya ugana chahiye",
        "kya ugana hai",

        "kaunsi fasal",
        "konsi fasal",
        "kon si fasal",

        "kitna pani",
        "kitni khaad",
        "kitna fertilizer",

        "profit kitna",
        "munafa kitna",

        "kya karun",
        "iska kya karun",
        "is ka kya karun",

        "yeh kya hai",
        "ye kya hai",
    ]

    agriculture_match = any(
        keyword in text
        for keyword in agriculture_keywords
    )

    greeting_match = any(
        greeting in text
        for greeting in greetings
    )

    follow_up_match = any(
        phrase in text
        for phrase in follow_up_questions
    )

    allowed = (
        agriculture_match
        or greeting_match
        or follow_up_match
    )

    if allowed:

        return GuardrailFunctionOutput(
            output_info=(
                "Input is relevant to Kisan Dost."
            ),
            tripwire_triggered=False,
        )

    return GuardrailFunctionOutput(
        output_info=(
            "Input is outside agricultural scope."
        ),
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

    if isinstance(input, str):

        text = input.lower()

    else:

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
            output_info=(
                "Dangerous pesticide or poisoning "
                "request detected."
            ),
            tripwire_triggered=True,
        )

    return GuardrailFunctionOutput(
        output_info=(
            "Pesticide safety check passed."
        ),
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

    # Empty response
    if not text.strip():

        return GuardrailFunctionOutput(
            output_info="Empty response detected.",
            tripwire_triggered=True,
        )

    # Extremely long response
    if len(text) > 12000:

        return GuardrailFunctionOutput(
            output_info=(
                "Response is excessively long."
            ),
            tripwire_triggered=True,
        )

    text_lower = text.lower()

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
        pattern in text_lower
        for pattern in unsafe_medical_patterns
    )

    pesticide_violation = any(
        pattern in text_lower
        for pattern in unsafe_pesticide_patterns
    )

    if (
        medical_violation
        or pesticide_violation
    ):

        return GuardrailFunctionOutput(
            output_info="Unsafe output detected.",
            tripwire_triggered=True,
        )

    return GuardrailFunctionOutput(
        output_info="Output passed validation.",
        tripwire_triggered=False,
    )


# =========================================================
# 4. KISAN DOST TRIAGE AGENT
# =========================================================

kisan_dost_agent = Agent(

    name="Kisan Dost",

    instructions="""

You are Kisan Dost, an AI agricultural
advisor for Pakistani farmers.

Answer in simple Urdu-English / Roman Urdu.

You help farmers with:

- crop selection
- fertilizer planning
- profit estimation
- mandi prices
- pest and disease guidance
- weather and irrigation
- government agriculture support

IMPORTANT:

1. Understand the farmer's question.

2. Preserve previous conversation context.

3. Do NOT ask the farmer to repeat
information already available.

4. If the question is about crops,
use the Agronomy Agent.

5. If the question is about pests or
crop diseases, use the Pest Agent.

6. If the question is about mandi,
prices or government support,
use the Market Agent.

7. If the question is about profit,
cost or financial estimation,
use the Finance Agent.

8. Never invent tool results.

9. If required information is missing,
ask only for the missing information.

10. Answer in simple Roman Urdu /
Urdu-English.

11. Be concise and practical.

12. Never provide human medical advice.

13. Never recommend pesticide ingestion.

14. For pesticide questions,
provide only safe agricultural guidance.

15. Clearly identify estimates.

16. Use existing farmer memory whenever
it is relevant.

""",

    model=model,

    handoffs=[
        agronomy_agent,
        pest_agent,
        market_agent,
        finance_agent,
    ],

    input_guardrails=[
        agriculture_input_guardrail,
        pesticide_safety_guardrail,
    ],

    output_guardrails=[
        output_validation_guardrail,
    ],

    output_type=KisanDostResponse,
)


# =========================================================
# 5. MAIN CHAT
# =========================================================

async def main():

    print()

    print("=" * 60)
    print("🌾 KISAN DOST — FARMER'S FRIEND")
    print("=" * 60)

    print()

    print(
        "👨‍🌾 Kisan Dost se baat karein."
    )

    print(
        "💡 Program band karne ke liye 'exit' likhein."
    )

    print(
        "🧠 Memory enabled."
    )

    print("-" * 60)

    # Load memory
    memory = load_memory()

    if memory:

        print(
            f"🧠 Previous conversation loaded: "
            f"{len(memory)} messages"
        )

    while True:

        try:

            question = input(
                "\n👨‍🌾 Farmer: "
            ).strip()

        except KeyboardInterrupt:

            print(
                "\n\n🤖 Kisan Dost: "
                "Allah Hafiz! 👋🌾"
            )

            break

        except EOFError:

            print(
                "\n\n🤖 Kisan Dost: "
                "Allah Hafiz! 👋🌾"
            )

            break

        # =================================================
        # EXIT
        # =================================================

        if question.lower() == "exit":

            print(
                "\n🤖 Kisan Dost: "
                "Allah Hafiz! 👋🌾"
            )

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
        # BUILD MEMORY CONTEXT
        # =================================================

        context = build_context(
            memory,
            question,
        )

        # =================================================
        # RUN AGENT
        # =================================================

        try:

            result = await Runner.run(
                kisan_dost_agent,
                context,
            )

            print(
                "\n🤖 Kisan Dost:"
            )

            print("-" * 60)

            final_output = result.final_output

            # =================================================
            # PYDANTIC RESPONSE
            # =================================================

            if isinstance(
                final_output,
                KisanDostResponse,
            ):

                answer = final_output.answer

                print(answer)

                if final_output.safety_note:

                    print(
                        f"\n⚠️ "
                        f"{final_output.safety_note}"
                    )

            else:

                answer = str(
                    final_output
                )

                print(answer)

            # =================================================
            # SAVE MEMORY
            # =================================================

            memory.append(
                {
                    "farmer": question,
                    "assistant": answer,
                }
            )

            save_memory(memory)

        # =================================================
        # INPUT GUARDRAIL
        # =================================================

        except InputGuardrailTripwireTriggered:

            print(
                "\n🛡️ Kisan Dost:"
            )

            print(
                "Maaf kijiye, main sirf farming "
                "aur agriculture-related questions "
                "mein madad kar sakta hoon. 🌾"
            )

        # =================================================
        # OUTPUT GUARDRAIL
        # =================================================

        except OutputGuardrailTripwireTriggered:

            print(
                "\n🛡️ Kisan Dost:"
            )

            print(
                "Response safety check pass "
                "nahi kar saka."
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
                "\n❌ Kisan Dost mein temporary "
                "error aa gaya."
            )

            print(
                "Please dobara try karein."
            )

            print(
                f"\nTechnical error: "
                f"{type(e).__name__}: {e}"
            )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())