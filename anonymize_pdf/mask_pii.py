import fitz
import re
import json
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider


class PresidioMasker:
    def __init__(self, output_dir=None):
        config = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}],
        }

        provider = NlpEngineProvider(nlp_configuration=config)
        nlp_engine = provider.create_engine()

        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        self.entity_counters = {}
        self.pii_map = {}
        self.output_dir = output_dir

    def extract_text_from_pdf(self, pdf_path):
        text = ""
        doc = fitz.open(pdf_path)

        for page in doc:
            text += page.get_text()

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        return text

    def _get_placeholder(self, entity):
        self.entity_counters[entity] = self.entity_counters.get(entity, 0) + 1
        return f"{entity}_{self.entity_counters[entity]}"

    def mask_pii(self, text):

        results = self.analyzer.analyze(
            text=text,
            entities=["PERSON", "DATE_TIME", "PHONE_NUMBER", "EMAIL_ADDRESS", "US_SSN"],
            language="en",
        )

        results = sorted(results, key=lambda x: x.start)

        masked = []
        last = 0

        for r in results:
            start, end = r.start, r.end

            original = text[start:end]
            if len(original.strip()) < 2:
                continue

            placeholder = self._get_placeholder(r.entity_type)

            masked.append(text[last:start])
            masked.append(placeholder)

            self.pii_map[placeholder] = original
            last = end

        masked.append(text[last:])
        masked_text = "".join(masked)

        # ✅ Hospital ID (custom)
        for m in re.finditer(r"HOSP\d+", masked_text):
            ph = self._get_placeholder("HOSPITAL_ID")
            masked_text = masked_text.replace(m.group(), ph, 1)
            self.pii_map[ph] = m.group()

        # ✅ Save mapping
        if self.output_dir:
            with open(f"{self.output_dir}/pii_map.json", "w") as f:
                json.dump(self.pii_map, f, indent=2)

        return masked_text, self.pii_map

    def unmask_text(self, text):
        for k in sorted(self.pii_map, key=len, reverse=True):
            text = text.replace(k, self.pii_map[k])
        return text