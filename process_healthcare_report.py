import os
import json
import re

from config import *
from anonymize_pdf.mask_pii import PresidioMasker
from gemini_integration import summarize_chunk


# ✅ Extract patient ID BEFORE LLM
def extract_patient_id(text):
    match = re.search(r"PERSON_\d+", text)
    return match.group() if match else "UNKNOWN"


def extract_dob(text):
    match = re.search(r"DATE_TIME_\d+", text)
    return match.group() if match else None


def remove_extra_dob(text):
    # ✅ Remove stray "DOB" without proper value
    text = re.sub(r"\bDOB\b(?!\s*:)", "", text)
    return text


# ✅ Split patients properly (CORE LOGIC)
def split_by_patient(text):

    pattern = r"Patient Demographics\s*.*?Name:\s*PERSON_\d+"
    matches = list(re.finditer(pattern, text, re.DOTALL))

    sections = []

    for i in range(len(matches)):
        start = matches[i].start()

        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(text)

        chunk = text[start:end].strip()
        sections.append((f"Patient {len(sections)+1}", chunk))

    return sections


# ✅ Fix broken names (after unmasking)
def clean_unmasked(text):
    text = re.sub(r"([A-Za-z])\n([A-Za-z])", r"\1 \2", text)
    return text


# ✅ MAIN PIPELINE
def main(pdf_path=None):

    print("🔧 Starting pipeline...")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    masker = PresidioMasker(output_dir=OUTPUT_DIR)

    # ✅ Extract + Mask
    path = pdf_path if pdf_path else PDF_PATH
    raw_text = masker.extract_text_from_pdf(path)

    masked_text, pii_map = masker.mask_pii(raw_text)

    # ✅ Save masked text
    with open(MASKED_TEXT_PATH, "w", encoding="utf-8") as f:
        f.write(masked_text)

    # ✅ Save mapping
    with open(PII_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(pii_map, f, indent=2)

    # ✅ Split patients (ONLY segmentation used)
    patient_sections = split_by_patient(masked_text)
    print(f"✅ Patients found: {len(patient_sections)}")

    # ✅ Clear old outputs
    open(SUMMARY_MASKED_PATH, "w").close()
    open(SUMMARY_UNMASKED_PATH, "w").close()

    # ✅ Process each patient
    for header, body in patient_sections:

        print(f"Processing: {header}")

        # ✅ Extract BEFORE LLM
        patient_id = extract_patient_id(body)
        dob = extract_dob(body)

        # ✅ ONE CALL PER PATIENT (no chunking)
        summary = summarize_chunk(body)

        # ✅ Handle quota / failure
        if not summary:
            summary = "⚠️ Skipped due to API quota limit"

        # ✅ Inject metadata
        if dob:
            summary = f"Patient: {patient_id}\nDOB: {dob}\n{summary}"
        else:
            summary = f"Patient: {patient_id}\n{summary}"

        # ✅ Masked output
        masked_output = f"{header}\n{summary}\n{'-'*40}\n"

        # ✅ Unmask safely
        unmasked_summary = masker.unmask_text(summary)
        unmasked_summary = clean_unmasked(unmasked_summary)
        unmasked_summary = remove_extra_dob(unmasked_summary)

        unmasked_output = f"{header}\n{unmasked_summary}\n{'-'*40}\n"

        # ✅ Save outputs
        with open(SUMMARY_MASKED_PATH, "a", encoding="utf-8") as f:
            f.write(masked_output)

        with open(SUMMARY_UNMASKED_PATH, "a", encoding="utf-8") as f:
            f.write(unmasked_output)

    print("✅ DONE")


if __name__ == "__main__":
    main()
