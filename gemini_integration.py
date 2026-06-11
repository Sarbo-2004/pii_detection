import google.generativeai as genai
import time
import threading
from config import GEMINI_API_KEY, GEMINI_MODEL

# ✅ Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# ✅ Rate limiter (15 RPM → ~4 sec gap)
lock = threading.Lock()
last_call_time = 0
MIN_INTERVAL = 4.2


# ✅ CENTRAL RATE CONTROL
def rate_limited_call():
    global last_call_time

    with lock:
        now = time.time()
        wait_time = MIN_INTERVAL - (now - last_call_time)

        if wait_time > 0:
            print(f"⏳ Waiting {wait_time:.2f}s to respect rate limit...")
            time.sleep(wait_time)

        last_call_time = time.time()


# ✅ CORE GEMINI CALL (IMPROVED)
def call_gemini(prompt, max_retries=3):
    for attempt in range(1, max_retries + 1):
        try:
            rate_limited_call()

            response = model.generate_content(prompt)

            if response and hasattr(response, "text") and response.text:
                return response.text.strip()

        except Exception as e:
            error_msg = str(e).lower()
            print(f"❌ Gemini error (attempt {attempt}): {e}")

            # ✅ Smart handling
            if "rate" in error_msg or "quota" in error_msg:
                wait_time = 10 * attempt  # exponential wait
                print(f"⏳ Rate/Quota hit. Waiting {wait_time}s...")
                time.sleep(wait_time)
            else:
                time.sleep(3)

    return None


# ✅ PATIENT-LEVEL SUMMARY
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


# ✅ ✅ NEW FUNCTION: OVERALL SUMMARIZER
def overall_summarizer(full_text):
    """
    Generates a combined summary across all patients
    """

    # ✅ Safety: avoid token overflow
    MAX_INPUT = 15000
    full_text = full_text[:MAX_INPUT]

    prompt = f"""
You are given summaries of multiple patients.

Generate ONE final overall summary.

STRICT RULES:
- Identify common diseases
- Merge repeated patterns
- Highlight trends
- Keep concise
- Do NOT repeat patient-by-patient info

FORMAT:

Overall Diagnosis Trends:
Common Findings:
Frequent Treatments:
General Outcomes:
Key Insights:

TEXT:
{full_text}
"""

    return call_gemini(prompt)
