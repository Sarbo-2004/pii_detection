import streamlit as st
import requests
import hashlib

API_URL = "http://127.0.0.1:8000/process"

st.set_page_config(page_title="Healthcare AI System", layout="wide")

st.title("🧠 Healthcare AI Summarization System")
st.write("Upload a healthcare PDF to generate structured clinical summaries.")

def process_file_no_cache(file_bytes):
    files = {"file": ("uploaded.pdf", file_bytes, "application/pdf")}
    response = requests.post(API_URL, files=files)
    if response.status_code == 200:
        return response.json()
    return {"status": "error", "message": "API failed"}

@st.cache_data
def process_file_cached(file_bytes):
    return process_file_no_cache(file_bytes)

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

def format_overall_summary(text):
    text = text.replace("Overall Diagnosis Trends:", "### 🧬 Overall Diagnosis Trends")
    text = text.replace("Common Findings:", "### 🔍 Common Findings")
    text = text.replace("Frequent Treatments:", "### 💊 Frequent Treatments")
    text = text.replace("General Outcomes:", "### 📈 General Outcomes")
    text = text.replace("Key Insights:", "### 🧠 Key Insights")
    text = text.replace("*", "-")
    return text

uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"])

if uploaded_file:
    st.success("✅ File uploaded")

    file_bytes = uploaded_file.read()
    file_hash = hashlib.md5(file_bytes).hexdigest()

    col1, col2 = st.columns(2)

    with col1:
        process_btn = st.button("🚀 Process Report")

    with col2:
        rerun_btn = st.button("🔁 Re-process (Ignore Cache)")

    if process_btn or rerun_btn:
        progress = st.progress(0)

        with st.spinner("Processing... ⏳"):
            progress.progress(20)

            if rerun_btn:
                result = process_file_no_cache(file_bytes)
            else:
                result = process_file_cached(file_bytes)

            progress.progress(80)

        if result["status"] == "success":
            progress.progress(100)
            st.success("✅ Processing Complete!")

            patient_text = result.get("patient_summaries", "")
            overall_text = result.get("overall_summary", "")

            if "Skipped due to API quota" in patient_text:
                st.warning("⚠️ Some patients were skipped. Click 'Re-process' to retry.")
                st.cache_data.clear()

            st.subheader("🧾 Overall Summary")

            if overall_text:
                formatted_overall = format_overall_summary(overall_text)
                st.markdown(formatted_overall)
            else:
                st.warning("⚠️ Overall summary not available")

            sections = format_output(patient_text)

            if "Skipped due to API quota" in patient_text and len(sections) <= 1:
                st.error("⚠️ Most summaries failed due to API limits. Please retry.")

            st.metric("Patients Processed", len(sections))

            st.subheader("📊 Patient Summaries")

            for i, section in enumerate(sections, 1):
                with st.expander(f"👤 Patient {i}", expanded=(i == 1)):
                    st.text(section)

            col1, col2 = st.columns(2)

            with col1:
                st.download_button(
                    "📥 Download Patient Summaries",
                    patient_text,
                    file_name="patient_summary.txt",
                    mime="text/plain"
                )

            with col2:
                st.download_button(
                    "📥 Download Overall Summary",
                    overall_text,
                    file_name="overall_summary.txt",
                    mime="text/plain"
                )

        else:
            st.error(f"❌ {result['message']}")
