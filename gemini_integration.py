import google.generativeai as genai
import time
from config import GEMINI_API_KEY, GEMINI_MODEL, API_DELAY, MAX_RETRIES

# ✅ Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)


# ✅ Core Gemini call
def call_gemini(prompt):
    for _ in range(MAX_RETRIES):
        try:
            res = model.generate_content(prompt)

            if res and hasattr(res, "text") and res.text:
                time.sleep(API_DELAY)
                return res.text.strip()

        except Exception as e:
            print("Gemini Error:", e)
            time.sleep(2)

    return None


# ✅ Summarize a SINGLE chunk
def summarize_chunk(text):
    prompt = f"""
Summarize the medical report.

STRICT RULES:
- Only medical information
- Do NOT include names or identifiers
- No repetition

Format:
Diagnosis:
Key Findings:
Treatment:
Outcome:

TEXT:
{text}
"""
    return call_gemini(prompt)