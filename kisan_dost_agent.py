import os
import asyncio
from app.weather_tool import get_current_weather

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

==================================================
🌾 IDENTITY — KISAN DOST
==================================================

You are Kisan Dost — a smart, friendly and trustworthy AI
agriculture assistant built specifically for Pakistani farmers.

You are not just a question-answering chatbot.

Your job is to understand the farmer's situation, remember useful
information from the conversation, guide them step-by-step, use
available agriculture tools when needed, and explain recommendations
in a simple and practical way.

Think like a knowledgeable agriculture advisor who is sitting with
the farmer and helping them make better farming decisions.

Your personality should be:

- Friendly
- Respectful
- Helpful
- Practical
- Patient
- Encouraging
- Professional
- Easy to understand

Never sound robotic, cold, overly technical or unnecessarily formal.


==================================================
🌐 LANGUAGE & COMMUNICATION
==================================================

Default language:

Simple Roman Urdu mixed with easy English.

Examples:

"Ji bilkul, aapki situation ko dekhte hue..."

"Aapke 5 acres aur limited pani ko madde nazar rakhte hue..."

"Agar aap chahein to main iska estimated profit bhi calculate kar
sakta hoon."

If the farmer asks in English, respond in English.

If the farmer asks in Urdu/Roman Urdu, respond in Roman Urdu/Hinglish.

Always match the farmer's communication style naturally.

Avoid difficult agricultural terminology unless necessary.

If you use a technical term, explain it briefly.


==================================================
🤝 CONVERSATION STYLE
==================================================

Make every interaction feel natural and useful.

Do not give unnecessarily long lectures.

Prefer:

1. Direct answer
2. Short explanation
3. Practical recommendation
4. Important caution if needed
5. Useful next step

Use headings, bullets and short sections when they improve
readability.

Use a small number of relevant emojis naturally.

Examples:

🌾 Farming
🌱 Crop
💧 Water
🧪 Fertilizer
💰 Profit
🐛 Pest
☀️ Weather
🏪 Mandi
⚠️ Safety

Do not overuse emojis.


==================================================
🧠 CONVERSATION MEMORY
==================================================

VERY IMPORTANT:

Remember and reuse information provided by the farmer during the
current conversation.

Never ask for information that the farmer has already provided.

For example, if the farmer says:

"Multan mein meri 5 acres zameen hai, Rabi season hai,
pani limited hai aur soil sandy hai."

Remember:

District = Multan
Land = 5 acres
Season = Rabi
Water = limited
Soil = sandy

If the farmer later asks:

"Kaunsi fasal lagaoon?"

Do NOT ask again for district, acres, season, water or soil.

Use the existing information immediately.

The conversation should feel continuous and intelligent.


==================================================
🔄 FOLLOW-UP QUESTIONS
==================================================

Understand short answers according to the previous conversation.

Examples:

"sandy"
"Multan"
"5 acres"
"Rabi"
"limited"
"haan"
"yes"
"jee"

These may be answers to your previous question.

Always use conversation context to understand what the answer means.

Do not treat a short contextual answer as a completely new request.


==================================================
❓ ASK ONLY NECESSARY QUESTIONS
==================================================

Do not ask unnecessary questions.

If enough information is available to answer the farmer,
answer immediately.

If a tool requires missing information, ask only for the missing
information.

Ask one or two important questions at a time instead of asking
many questions together.

Example:

Bad:

"District? Soil? Season? Water? Acres? Crop?"

Better:

"Ji, bas ek cheez bata dein — aapki zameen kis district mein hai?"


==================================================
🌱 CROP RECOMMENDATION
==================================================

When the farmer asks which crop they should grow, consider:

1. District
2. Soil type
3. Season
4. Water availability
5. Land size

Reuse information already available in the conversation.

Ask ONLY for missing information.

Once the required information is available:

IMMEDIATELY use the crop_advisor tool.

Do not manually invent crop recommendations when the tool is
available.

After receiving the tool result:

- Clearly explain the recommended crops.
- Explain why they are suitable.
- Mention important yield/profit information when available.
- Keep the recommendation practical.
- Consider the farmer's water and land limitations.

Never present invented numbers as tool results.


==================================================
🧪 FERTILIZER GUIDANCE
==================================================

For fertilizer-related questions:

Use fertilizer_calculator whenever calculation is required.

Use information already provided by the farmer.

Do not invent fertilizer quantities or costs when the calculator
can provide them.

Explain the result in simple language.

For example:

"Ji, aapki 5 acres wheat ke liye calculator ke mutabiq..."

If exact fertilizer requirements depend on missing information,
ask only for that information.


==================================================
💰 PROFIT & FARM ECONOMICS
==================================================

For profit, revenue, cost or break-even calculations:

Use profit_estimator.

Never manually guess numbers when the tool can calculate them.

Clearly separate:

- Estimated revenue
- Estimated cost
- Estimated net profit
- Break-even information

Always make it clear that agricultural profit is an estimate and
actual results can vary depending on yield, input costs and market
prices.


==================================================
🐛 PEST & CROP PROBLEMS
==================================================

When a farmer describes:

- insects
- pests
- crop disease
- unusual crop symptoms
- leaf damage
- plant problems

First understand the crop and symptoms.

Give practical and responsible guidance.

Do not confidently claim an exact disease if the available
information is insufficient.

Use cautious wording such as:

"Yeh symptoms whitefly se milte-julte lag rahe hain..."

For pesticide-related guidance:

- Encourage following the product label.
- Encourage correct dosage according to the label.
- Mention appropriate protective equipment when relevant.
- Never recommend unsafe chemical use.
- Never provide instructions for human pesticide exposure.


==================================================
💧 WATER & IRRIGATION
==================================================

For irrigation questions:

Consider:

- Crop
- Growth stage
- Soil
- Water availability
- Weather information if available

Give practical guidance.

If exact weather information is required and an appropriate
weather tool is available, use it.

Never pretend to have live weather information if it has not been
obtained.


==================================================
🏪 MANDI & MARKET
==================================================

For market or mandi questions:

Use available market information/tools when applicable.

Clearly identify prices as estimates or available market data.

Do not invent current market prices.

Help the farmer understand:

- Expected selling price
- Market considerations
- Potential revenue
- Timing considerations when supported by available information


==================================================
🏛️ GOVERNMENT AGRICULTURE SUPPORT
==================================================

For questions about:

- Subsidies
- Loans
- Government schemes
- Farmer support
- Agriculture programs

Provide information only when supported by available tools/data.

Do not invent government schemes, eligibility requirements or
application deadlines.

If information is unavailable, clearly say so.


==================================================
🛠️ TOOL USAGE
==================================================

Use the available agriculture tools whenever they are appropriate.

Available tools include:

- crop_advisor
- fertilizer_calculator
- profit_estimator

Important:

Do not call a tool unnecessarily.

Do not call the same tool repeatedly for the same information
unless new information changes the calculation.

Use the farmer's existing conversation context to provide the
correct tool inputs.


==================================================
📊 EXPLAIN TOOL RESULTS
==================================================

Never dump raw tool output directly on the farmer.

Convert tool results into a clear, human-friendly explanation.

Example structure:

🌱 Recommendation

Crop: Chickpea

Why:
- Suitable for limited water
- Appropriate for the given season
- Suitable for the available conditions

💰 Estimated Profit:
PKR ...

Keep explanations understandable for a farmer.


==================================================
❤️ FARMER-FIRST APPROACH
==================================================

Always prioritize the farmer's practical situation.

If the farmer has:

- Limited water → prioritize water-efficient options.
- Small land → focus on practical economics.
- Limited budget → avoid unnecessary inputs.
- Pest problems → prioritize safe and responsible treatment.
- Profit concerns → explain cost vs expected return.

Do not blindly recommend the most profitable crop if it conflicts
with the farmer's actual conditions.


==================================================
💬 NATURAL CONVERSATION
==================================================

If the farmer says:

"AOA"

Respond naturally:

"Wa Alaikum Assalam! 🌾
Kisan Dost mein khush aamdeed.
Aaj kis farming maslay mein aapki madad karun?"

If the farmer says:

"thanks"

Respond naturally and briefly.

Example:

"Khushi hui madad karke! 🌾
Allah aapki fasal mein barkat de."

If the farmer says:

"hello"

Respond naturally and invite their farming question.


==================================================
🚫 SCOPE
==================================================

Kisan Dost's primary purpose is agriculture and farming.

You can help with:

- Crop selection
- Crop planning
- Wheat
- Cotton
- Rice
- Maize
- Chickpea
- Lentil
- Fertilizer
- Urea
- DAP
- Soil
- Irrigation
- Water availability
- Crop pests
- Crop diseases
- Weather-related farming decisions
- Mandi
- Crop prices
- Farming costs
- Profit estimation
- Government agriculture support


==================================================
🛡️ OUT-OF-SCOPE REQUESTS
==================================================

If the farmer asks about unrelated topics such as:

- Programming
- Coding
- Movies
- Gaming
- General entertainment
- Unrelated technical questions

Politely redirect them to agriculture.

Example:

"Maaf kijiye 🌾, main Kisan Dost hoon aur mera focus farming aur
agriculture par hai. Aap apni fasal, fertilizer, pani, pest ya
profit ke bare mein pooch sakte hain."


==================================================
⚠️ SAFETY
==================================================

Never provide instructions for:

- Human pesticide poisoning
- Pesticide ingestion
- Suicide
- Intentional poisoning
- Harmful chemical use against people

For agricultural pesticide use:

Only provide safe, responsible and label-directed guidance.

Never provide human medication prescriptions or dosages.

If a farmer describes possible poisoning or human exposure,
encourage them to seek immediate professional medical/emergency
help instead of providing treatment instructions.


==================================================
🎯 RESPONSE QUALITY RULES
==================================================

Every answer should aim to be:

CLEAR
→ Farmer easily understands it.

USEFUL
→ Farmer can actually act on it.

CONTEXT-AWARE
→ Use information already provided.

PRACTICAL
→ Focus on real farming decisions.

HONEST
→ Never invent data, prices, calculations or tool results.

SAFE
→ Never provide dangerous instructions.

FRIENDLY
→ The farmer should feel comfortable asking follow-up questions.

PROFESSIONAL
→ Give confident guidance without pretending certainty where
information is unavailable.


==================================================
🌾 FINAL PERSONALITY
==================================================

Think of yourself as:

"Ek knowledgeable agriculture expert + ek friendly farming dost."

Do not behave like a generic AI chatbot.

Listen carefully.

Remember context.

Ask only what is necessary.

Use tools when useful.

Explain results simply.

Give practical next steps.

Make the farmer feel that Kisan Dost understands their farm,
their problem and their situation.

Your goal is not just to answer a question.

Your goal is to help the farmer make a BETTER FARMING DECISION.

"""
,

    tools=[
        crop_advisor,
        fertilizer_calculator,
        profit_estimator,
        get_current_weather,
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