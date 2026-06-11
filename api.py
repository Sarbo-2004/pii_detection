from fastapi import FastAPI, UploadFile, File
import shutil
import os
import uuid

from process_healthcare_report import main as run_pipeline
from gemini_integration import overall_summarizer
from config import OUTPUT_DIR, SUMMARY_UNMASKED_PATH

app = FastAPI(title="Healthcare AI Summarization API")

TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.post("/process")
async def process_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(TEMP_DIR, f"{file_id}.pdf")

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        run_pipeline(pdf_path=file_path)

        if not os.path.exists(SUMMARY_UNMASKED_PATH):
            return {"status": "error", "message": "Summary file not found"}

        with open(SUMMARY_UNMASKED_PATH, "r", encoding="utf-8") as f:
            summary = f.read().strip()

        if not summary:
            return {"status": "error", "message": "No summaries generated"}

        cleaned_text = summary.replace("-" * 40, "")

        overall_summary = overall_summarizer(cleaned_text)

        if not overall_summary:
            overall_summary = "⚠️ Could not generate overall summary due to API limits."

        overall_path = os.path.join(OUTPUT_DIR, "overall_summary.txt")
        with open(overall_path, "w", encoding="utf-8") as f:
            f.write(overall_summary)

        os.remove(file_path)

        return {
            "status": "success",
            "patient_summaries": summary,
            "overall_summary": overall_summary
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
