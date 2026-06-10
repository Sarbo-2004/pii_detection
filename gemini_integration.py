import google.generativeai as genai
import time
import threading
from config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# ✅ Rate limiter (15 RPM → 1 call every ~4 sec)
lock = threading.Lock()
last_call_time = 0
MIN_INTERVAL = 4.2


def rate_limited_call():
    global last_call_time

    with lock:
        now = time.time()
        wait_time = MIN_INTERVAL - (now - last_call_time)

        if wait_time > 0:
            print(f"⏳ Waiting {wait_time:.2f}s...")
            time.sleep(wait_time)

        last_call_time = time.time()


def call_gemini(prompt):
    for attempt in range(3):
        try:
            rate_limited_call()

            res = model.generate_content(prompt)

            if res and res.text:
                return res.text.strip()

        except Exception as e:
            print("Gemini error:", e)

            if "rate" in str(e).lower():
                time.sleep(10)

    return None


def summarize_chunk(text):
    prompt = f"""
Summarize the medical report.

STRICT RULES:
- Only medical information
- No identifiers
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