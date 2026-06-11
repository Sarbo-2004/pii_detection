from gemini_integration import overall_summarizer
from config import OUTPUT_DIR

def main():

    input_file = f"{OUTPUT_DIR}/final_output.txt"
    output_file = f"{OUTPUT_DIR}/overall_summary.txt"

    print("Reading final output file...")

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # ✅ Clean separators (important)
    text = text.replace("-" * 40, "")

    print("Generating overall summary...")

    overall = overall_summarizer(text)

    if not overall:
        overall = "⚠️ Could not generate summary due to API limits."

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(overall)

    print(f"✅ Overall summary saved at: {output_file}")


if __name__ == "__main__":
    main()