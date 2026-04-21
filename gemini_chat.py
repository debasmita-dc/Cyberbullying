from dotenv import load_dotenv
from pathlib import Path
import os
from google import genai

# Load .env from same folder as this file (reliable)
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Create Gemini client (reads GEMINI_API_KEY env var if not passed explicitly)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_INSTRUCTIONS = """
You are a fast, helpful chatbot embedded in a cyberbullying detection web app.

Rules:
- Handle contradictions: if user says X then later says not X, explain both and ask 1 short clarifying question.
- Handle negation carefully ("not bad" != "bad").
- Understand jokes/fun; switch serious when user asks for help or mentions threats/harm.
- Keep replies concise (2–6 lines) unless user asks for detail.
- If user asks about the app: explain how to use Detect/Report/Legal/Dashboard.
- Safety: do not encourage harassment, threats, wrongdoing; suggest respectful alternatives.
"""

def generate_reply(user_text: str, history: list[dict], model: str = "gemini-2.5-flash") -> tuple[str, list[dict]]:
    """
    history: list of Gemini 'Content' dicts:
      {"role":"user"|"model", "parts":[{"text":"..."}]}
    """
    text = (user_text or "").strip()
    if not text:
        return "Say something and I’ll help 🙂", history

    # Build conversation contents: system + recent history + new user message
    contents = []
    contents.append({"role": "user", "parts": [{"text": f"(System)\n{SYSTEM_INSTRUCTIONS}"}]})
    contents.extend(history[-10:])
    contents.append({"role": "user", "parts": [{"text": text}]})

    # Generate content
    resp = client.models.generate_content(
        model=model,
        contents=contents
    )

    reply = (getattr(resp, "text", "") or "").strip()
    if not reply:
        reply = "I didn’t catch that—can you rephrase in one line?"

    # Update history
    new_history = history + [
        {"role": "user", "parts": [{"text": text}]},
        {"role": "model", "parts": [{"text": reply}]},
    ]
    return reply, new_history[-20:]