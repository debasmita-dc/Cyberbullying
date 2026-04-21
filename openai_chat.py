'''from dotenv import load_dotenv
from pathlib import Path
import os
from openai import OpenAI

#load_dotenv()  # loads .env file

# Load .env from the SAME folder as openai_chat.py (reliable)
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Optional debug (prints True/False only, not the key)
print("OPENAI_API_KEY loaded?", bool(os.getenv("OPENAI_API_KEY")))

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # env-based key :contentReference[oaicite:1]{index=1}

SYSTEM_INSTRUCTIONS = """
You are a fast, helpful chatbot embedded in a cyberbullying detection web app.

Goals:
- Handle contradictions: if user says X then says not X, ask 1 short clarifying question OR explain both interpretations.
- Handle negation carefully ("not bad" != "bad").
- Handle jokes/fun: respond playfully, but if user asks serious help, switch tone.
- Be concise by default (2–6 lines), unless the user asks for detail.
- If user asks about the app: explain how to use detect/report/legal dashboard etc.
- Safety: refuse instructions for wrongdoing, harassment, threats. Encourage respectful behavior.

Style:
- Simple language, quick, practical.
"""

def generate_reply(user_text: str, previous_response_id: str | None = None, model: str = "gpt-5.2"):
    """
    Uses OpenAI Responses API. Keeps conversation state using previous_response_id.
    """
    if not user_text or not user_text.strip():
        return ("Say something and I’ll help 🙂", previous_response_id)

    resp = client.responses.create(
        model=model,
        instructions=SYSTEM_INSTRUCTIONS,  # include each time (instructions don't carry automatically) :contentReference[oaicite:2]{index=2}
        previous_response_id=previous_response_id,
        input=user_text,
        max_output_tokens=250,
    )

    # Python SDK convenience: resp.output_text contains aggregated assistant text :contentReference[oaicite:3]{index=3}
    assistant_text = (getattr(resp, "output_text", "") or "").strip()
    new_prev = getattr(resp, "id", None)

    if not assistant_text:
        assistant_text = "I didn’t catch that—can you rephrase in one line?"

    return (assistant_text, new_prev) '''