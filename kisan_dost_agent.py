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
    RunContextWrapper,
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

# =========================================
# model
# =========================================

model = OpenAIChatCompletionsModel(
    model="openrouter/free",
    openai_client=client,
)


# =========================================================
# AGRICULTURE INPUT GUARDRAIL
# =========================================================

@input_guardrail
async def agriculture_input_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    input: str | list,
) -> GuardrailFunctionOutput:

    user_input = str(input).lower().strip()

    # -----------------------------------------------------
    # Greetings
    # -----------------------------------------------------

    greetings = [
        "aoa",
        "assalam o alaikum",
        "assalamualaikum",
        "salam",
        "hello",
        "hi",
        "hey",
        "ao",
        "walekum salam",
        "walaikum salam",
    ]

    if any(greeting in user_input for greeting in greetings):

        return GuardrailFunctionOutput(
            output_info="Greeting",
            tripwire_triggered=False,
        )


    # -----------------------------------------------------
    # Agriculture keywords
    # -----------------------------------------------------

    agriculture_keywords = [

        # General agriculture
        "crop",
        "crops",
        "fasal",
        "faslen",
        "farming",
        "kheti",
        "agriculture",
        "agri",
        "farmer",
        "kisan",
        "zameen",
        "land",
        "field",
        "khet",

        # Soil
        "soil",
        "mitti",
        "loam",
        "loamy",
        "sindhi loam",
        "sindhi",
        "rehri",
        "rehri wali mitti",
        "clay",
        "clayey",
        "kliwi",
        "kliwi mitti",
        "ghareeli mitti",
        "sandy",
        "sand",
        "sandy soil",
        "patli mitti",
        "reti wali mitti",
        "silty",
        "silt",
        "silty soil",

        # Crops
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
        "millet",
        "bajra",
        "sorghum",
        "jowar",

        # Fertilizer
        "fertilizer",
        "fertiliser",
        "khaad",
        "khad",
        "urea",
        "dap",
        "npk",

        # Pest / disease
        "pesticide",
        "spray",
        "pest",
        "keet",
        "keera",
        "insect",
        "disease",
        "bimari",
        "fungus",

        # Weather / irrigation
        "weather",
        "mausam",
        "rain",
        "barish",
        "irrigation",
        "sinchai",
        "pani",
        "water",
        "limited",
        "adequate",
        "low water",
        "very low",

        # Market
        "mandi",
        "price",
        "rate",
        "selling",
        "market",

        # Profit
        "profit",
        "munafa",
        "faida",
        "yield",
        "paidawar",
        "cost",
        "kharcha",
        "income",

        # Government
        "subsidy",
        "loan",
        "government",
        "scheme",
        "support",

        # Location / farming details
        "district",
        "multan",
        "faisalabad",
        "lahore",
        "bahawalpur",
        "sahiwal",
        "punjab",
        "acre",
        "acres",
        "season",
        "rabi",
        "kharif",
        "winter",
        "summer",
        "monsoon",
    ]


    # -----------------------------------------------------
    # Agriculture-related input
    # -----------------------------------------------------

    if any(
        keyword in user_input
        for keyword in agriculture_keywords
    ):

        return GuardrailFunctionOutput(
            output_info="Agriculture-related input",
            tripwire_triggered=False,
        )


    # -----------------------------------------------------
    # Short follow-up answers
    # -----------------------------------------------------
    # Important:
    # sandy
    # Multan
    # Faisalabad
    # 5 acres
    # Rabi
    # limited
    # yes
    # haan
    #
    # These should NOT be blocked.
    # -----------------------------------------------------

    follow_up_answers = [
        "yes",
        "no",
        "haan",
        "han",
        "ji",
        "jee",
        "nahin",
        "nahi",
        "theek",
        "theek hai",
        "sandy",
        "sand",
        "clay",
        "clayey",
        "loam",
        "loamy",
        "silty",
        "silt",
        "rabi",
        "kharif",
        "limited",
        "adequate",
        "low",
        "multan",
        "faisalabad",
        "lahore",
        "bahawalpur",
        "sahiwal",
        "5 acres",
        "10 acres",
        "1 acre",
        "2 acres",
        "3 acres",
        "4 acres",
    ]

    if user_input in follow_up_answers:

        return GuardrailFunctionOutput(
            output_info="Follow-up answer",
            tripwire_triggered=False,
        )


    # -----------------------------------------------------
    # Very short answers
    # -----------------------------------------------------

    if len(user_input.split()) <= 3:

        return GuardrailFunctionOutput(
            output_info="Possible follow-up answer",
            tripwire_triggered=False,
        )


    # -----------------------------------------------------
    # Clearly unrelated topics
    # -----------------------------------------------------

    unrelated_keywords = [
        "python programming",
        "write python code",
        "python code",
        "javascript programming",
        "html code",
        "css code",
        "movie review",
        "football match",
        "cricket score",
        "gaming",
    ]

    if any(
        keyword in user_input
        for keyword in unrelated_keywords
    ):

        return GuardrailFunctionOutput(
            output_info="Non-agriculture topic detected",
            tripwire_triggered=True,
        )


    # -----------------------------------------------------
    # Allow normal conversation
    # -----------------------------------------------------

    return GuardrailFunctionOutput(
        output_info="Conversational input",
        tripwire_triggered=False,
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


    # Empty response
    if not text.strip():

        return GuardrailFunctionOutput(
            output_info="Empty response detected.",
            tripwire_triggered=True,
        )


    # Extremely long response
    if len(text) > 12000:

        return GuardrailFunctionOutput(
            output_info="Response is excessively long.",
            tripwire_triggered=True,
        )


    # Unsafe medical / pesticide content
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

You are Kisan Dost, an AI farming assistant for Pakistani farmers.

Your primary purpose is to help Pakistani farmers with agriculture
and farming questions.

==================================================
LANGUAGE
==================================================

Always answer in simple Roman Urdu/Hinglish unless the farmer
specifically asks for English or another language.

Be friendly, practical and easy to understand.

==================================================
CONVERSATION MEMORY
==================================================

VERY IMPORTANT:

Use all information already provided by the farmer in the
current conversation.

NEVER ask again for information that the farmer has already given.

For example, if the farmer says:

"Multan mein 5 acres zameen hai, Rabi season hai,
pani limited hai aur soil sandy hai."

You must remember:

District = Multan
Land = 5 acres
Season = Rabi
Water = limited
Soil = sandy

Do NOT ask for these details again.

==================================================
FOLLOW-UP ANSWERS
==================================================

A short answer can be an answer to your previous question.

Examples:

"sandy"
"clay"
"loamy"
"silty"
"Multan"
"Faisalabad"
"5 acres"
"Rabi"
"Kharif"
"limited"
"adequate"
"haan"
"yes"

Treat these as follow-up answers and use the previous conversation
to understand what information they refer to.

==================================================
CROP RECOMMENDATION
==================================================

When the farmer asks which crop to grow, collect these details:

1. District
2. Soil type
3. Season
4. Water availability
5. Land size in acres

If some details are already available in the conversation,
reuse them.

Ask ONLY for the missing information.

When all required information is available, immediately use
the crop_advisor tool.

Do NOT repeatedly ask the same question.

==================================================
FERTILIZER
==================================================

For fertilizer questions, use fertilizer_calculator when
calculation is required.

Use information already provided by the farmer.

==================================================
PROFIT
==================================================

For profit calculations, use profit_estimator.

Do not make up calculations when the tool can calculate them.

==================================================
AVAILABLE TOPICS
==================================================

You can help with:

- Crop selection
- Wheat
- Cotton
- Rice
- Maize
- Chickpea
- Lentil
- Fertilizer
- Urea
- DAP
- Crop profit
- Farming cost
- Soil
- Irrigation
- Water availability
- Pests
- Crop diseases
- Weather-related farming questions
- Mandi
- Crop prices
- Government agriculture support

==================================================
IMPORTANT
==================================================

If the farmer asks an agriculture question, answer it.

If a tool is appropriate, use the tool.

Do not simply explain that you need information if all required
information has already been provided.

Do not repeatedly ask:

"What is your district?"
"What is your soil type?"
"What is your season?"
"What is your water availability?"
"What is your land size?"

If the information is already available, use it.

==================================================
SAFETY
==================================================

Never provide instructions for human pesticide poisoning,
pesticide ingestion, suicide or harmful chemical use.

For agricultural pesticide use, provide only safe,
label-directed and responsible guidance.

"""
,

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
# TERMINAL CHAT
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


    # Conversation history
    conversation = []


    while True:

        try:

            question = input(
                "\n👨‍🌾 Farmer: "
            ).strip()

        except (KeyboardInterrupt, EOFError):

            print(
                "\n\n🤖 Kisan Dost: Allah Hafiz! 👋🌾"
            )

            break


        if question.lower() == "exit":

            print(
                "\n🤖 Kisan Dost: Allah Hafiz! 👋🌾"
            )

            break


        if not question:

            print(
                "\n🤖 Kisan Dost: Please apna question likhein."
            )

            continue


        # Add user message
        conversation.append({
            "role": "user",
            "content": question,
        })


        try:

            result = await Runner.run(
                kisan_dost_agent,
                conversation,
            )


            final_output = result.final_output


            # Save assistant response
            conversation.append({
                "role": "assistant",
                "content": str(final_output),
            })


            print()

            print("🤖 Kisan Dost:")

            print("-" * 60)

            print(final_output)


        except InputGuardrailTripwireTriggered:

            print()

            print("🛡️ Kisan Dost:")

            print(
                "Maaf kijiye, main sirf farming aur "
                "agriculture-related questions mein "
                "madad kar sakta hoon. 🌾"
            )


        except OutputGuardrailTripwireTriggered:

            print()

            print("🛡️ Kisan Dost:")

            print(
                "Response safety check pass nahi kar saka."
            )

            print(
                "Main safe agricultural guidance "
                "provide kar sakta hoon. 🌾"
            )


        except Exception as e:

            print()

            print(
                "❌ Kisan Dost mein error aa gaya."
            )

            print(
                f"Technical error: {type(e).__name__}"
            )

            print(
                f"Details: {str(e)}"
            )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    asyncio.run(main())