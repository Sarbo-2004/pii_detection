import os

# Health Report Settings
PDF_PATH = os.path.join("data", "HealthCare_Reports.pdf")

# Output settings
OUTPUT_DIR = "output"
MASKED_TEXT_PATH = os.path.join(OUTPUT_DIR, "masked_text.txt")
SUMMARY_MASKED_PATH = os.path.join(OUTPUT_DIR, "summary_masked.txt")
SUMMARY_UNMASKED_PATH = os.path.join(OUTPUT_DIR, "summary_unmasked.txt")
RESULT_JSON_PATH = os.path.join(OUTPUT_DIR, "result.json")
PII_MAP_PATH = os.path.join(OUTPUT_DIR, "pii_map.js")

# LLM Settings (using newer google genai client)

import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = "gemini-flash-lite-latest"
MAX_TOKENS = 2000

# Optional tuning settings
API_TEMPERATURE = 0.2
API_TOP_P = 0.95


CHUNK_SIZE = 3000
CHUNK_OVERLAP = 200
BATCH_SIZE = 2

API_DELAY = 2  # seconds
MAX_RETRIES = 3
