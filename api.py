from fastapi import FastAPI, UploadFile, File
import shutil
import os
import uuid

from process_healthcare_report import main as run_pipeline
from config import OUTPUT_DIR, SUMMARY_UNMASKED_PATH

# ✅ Initialize FastAPI app
app = FastAPI(title="Healthcare AI Summarization API")

# ✅ Temporary upload folder
TEMP_DIR = "temp_uploads"
os.makedirs(TEMP_DIR, exist_ok=True)


@app.post("/process")
async def process_file(file: UploadFile = File(...)):

    try:
        # ✅ Generate unique file name
        file_id = str(uuid.uuid4())
        file_path = os.path.join(TEMP_DIR, f"{file_id}.pdf")

        # ✅ Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ✅ Run pipeline with dynamic input
        run_pipeline(pdf_path=file_path)

        # ✅ Read output summary
        if os.path.exists(SUMMARY_UNMASKED_PATH):
            with open(SUMMARY_UNMASKED_PATH, "r", encoding="utf-8") as f:
                summary = f.read()

            return {
                "status": "success",
                "summary": summary
            }

        return {
            "status": "error",
            "message": "Summary file not found"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
