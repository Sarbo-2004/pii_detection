import streamlit as st
import requests
import hashlib

# 🔗 FastAPI endpoint
API_URL = "http://127.0.0.1:8000/process"

# ✅ Page config
st.set_page_config(page_title="Healthcare AI System", layout="wide")

st.title("🧠 Healthcare AI Summarization System")
st.write("Upload a healthcare PDF to generate structured clinical summaries.")

# ========================
# ✅ API CALL (NO CACHE)
# ========================
def process_file_no_cache(file_bytes):
    files = {"file": ("uploaded.pdf", file_bytes, "application/pdf")}
    response = requests.post(API_URL, files=files)

    if response.status_code == 200:
        return response.json()

    return {"status": "error", "message": "API failed"}


# ========================
# ✅ CACHED API CALL
# ========================
@st.cache_data
def process_file_cached(file_bytes):
    return process_file_no_cache(file_bytes)


# ========================
# ✅ FORMAT OUTPUT
# ========================
def format_output(text):
    sections = text.split("----------------------------------------")

    formatted = []

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue

        sec = sec.replace("Diagnosis:", "🧬 Diagnosis:\n")
        sec = sec.replace("Key Findings:", "🔍 Key Findings:\n")
        sec = sec.replace("Treatment:", "💊 Treatment:\n")
        sec = sec.replace("Outcome:", "📈 Outcome:\n")

        formatted.append(sec)

    return formatted


# ========================
# ✅ FILE UPLOAD
# ========================
uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])

if uploaded_file:

    st.success("✅ File uploaded")

    file_bytes = uploaded_file.read()

    # ✅ Hash for cache key
    file_hash = hashlib.md5(file_bytes).hexdigest()

    # ✅ Buttons
    col1, col2 = st.columns(2)

    with col1:
        process_btn = st.button("🚀 Process Report")

    with col2:
        rerun_btn = st.button("🔁 Re-process (Ignore Cache)")

    # ========================
    # ✅ PROCESS LOGIC
    # ========================
    if process_btn or rerun_btn:

        progress = st.progress(0)

        with st.spinner("Processing... ⏳"):

            progress.progress(20)

            # ✅ Decide cache or fresh call
            if rerun_btn:
                result = process_file_no_cache(file_bytes)
            else:
                result = process_file_cached(file_bytes)

            progress.progress(80)

        # ========================
        # ✅ HANDLE RESULT
        # ========================
        if result["status"] == "success":

            progress.progress(100)
            st.success("✅ Processing Complete!")

            raw_text = result["summary"]

            # ✅ Detect partial failures
            if "Skipped due to API quota" in raw_text:
                st.warning("⚠️ Some patients were skipped due to API quota. Click 'Re-process' to retry.")
                st.cache_data.clear()  # ✅ auto reset cache

            sections = format_output(raw_text)

            # ✅ Metrics
            st.metric("Patients Processed", len(sections))

            st.subheader("📊 Patient Summaries")

            # ✅ Expandable UI
            for i, section in enumerate(sections, 1):
                with st.expander(f"👤 Patient {i}", expanded=(i == 1)):
                    st.text(section)

            # ✅ Download button
            st.download_button(
                "📥 Download Full Report",
                raw_text,
                file_name="patient_summary.txt",
                mime="text/plain"
            )

        else:
            st.error(f"❌ {result['message']}")