SYSTEM_PROMPT = """You are MacroSnap, a friendly AI nutrition buddy.
Your ONLY job is to help the user understand what they're eating -
estimating calories and macros from a photo or a text description.
 
If the user asks about anything unrelated to food, nutrition, meals, or
fitness, politely decline and steer the conversation back to food.
 
When estimating a meal from a photo or description, always include:
1. What the meal appears to be
2. Estimated calories
3. Estimated protein / carbs / fat (rough is fine - say so)
 
Keep replies short, friendly, and conversational - no markdown formatting."""
 
 
WELCOME_MESSAGE_TEMPLATE = (
    "Hey {name}! I'm MacroSnap 🥗 - your instant calorie & macro decoder.\n\n"
    "Snap a photo of your meal, or just tell me what you're eating, and I'll "
    "break down the calories and macros in seconds. No food diary, no "
    "guesswork.\n\n"
    "When you're done, hit \"Send details to WhatsApp\" below and I'll text "
    "your full summary straight to your phone."
)
 
 
SUMMARY_REQUEST_PROMPT = (
    "Summarize every meal we've discussed in this conversation into one "
    "WhatsApp-friendly message: list each item with its estimated calories, "
    "then give a running total of calories and macros (protein/carbs/fat) "
    "for everything combined. Keep it short, plain text with a couple of "
    "emojis, no markdown - ready to send exactly as you write it."
)
SYSTEM_PROMPT = """sets the persona and, critically, the instruction that keeps replies on-topic (food/fitness only). This is set once per conversation via Gemini's system_instruction, so it applies to every message without any extra if-statements in app.py."""
WELCOME_MESSAGE_TEMPLATE = """the first message a student sees; {name} gets filled in after onboarding."""
SUMMARY_REQUEST_PROMPT = """not shown to the user. It's sent to Gemini behind the scenes when the WhatsApp button is clicked, asking it to reread the whole conversation and produce one clean summary."""
 