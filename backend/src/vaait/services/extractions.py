from typing import Any

from backend.src.vaait.settings import app
from gliner import GLiNER
from transformers import AutoTokenizer

device = app.DEVICE
compute_type = "int8"

tokenizer = AutoTokenizer.from_pretrained("Clinical-AI-Apollo/Medical-NER")
gliner_model = GLiNER.from_pretrained("urchade/gliner_large").to(device)
LABELS = [
    "ACTIVITY",
    "ADMINISTRATION",
    "AGE",
    "AREA",
    "BIOLOGICAL_ATTRIBUTE",
    "BIOLOGICAL_STRUCTURE",
    "CLINICAL_EVENT",
    "COLOR",
    "COREFERENCE",
    "DATE",
    "DETAILED_DESCRIPTION",
    "DIAGNOSTIC_PROCEDURE",
    "DISEASE_DISORDER",
    "DISTANCE",
    "DOSAGE",
    "DURATION",
    "FAMILY_HISTORY",
    "FREQUENCY",
    "HEIGHT",
    "HISTORY",
    "LAB_VALUE",
    "MASS",
    "MEDICATION",
    "NONBIOLOGICAL_LOCATION",
    "OCCUPATION",
    "OTHER_ENTITY",
    "OTHER_EVENT",
    "OUTCOME",
    "PERSONAL_BACKGROUND",
    "QUALITATIVE_CONCEPT",
    "SEVERITY",
    "SEX",
    "SHAPE",
    "SIGN_SYMPTOM",
    "SUBJECT",
    "TEXTURE",
    "THERAPEUTIC_PROCEDURE",
    "TIME",
    "VOLUME",
    "WEIGHT",
]

def extract_entities_with_gliner(soap_report: str) -> list[dict[str, Any]]:
    result = gliner_model.predict_entities(soap_report, LABELS, threshold=0.2)
    return [
        {"entity_group": entity["label"], "start": entity["start"], "end": entity["end"], "word": entity["text"]}
        for entity in result
    ]


def extract_entities_with_gliner_by_chunk(transcript: str, chunk_size: int = 200, overlap_token: int = 3) -> list[dict[str, Any]]:
    token = tokenizer(transcript)["input_ids"][1:-1]
    token_len = len(tokenizer(transcript)["input_ids"])

    entities = []
    start_index = 0
    while start_index < token_len:
        end_index = min(start_index + chunk_size, token_len)

        input_chunk = token[start_index:end_index]
        input_txt = tokenizer.decode(input_chunk)
        result = gliner_model.predict_entities(input_txt, LABELS, threshold=0.2)
        entities.extend(result)

        start_index += chunk_size - overlap_token

    return [{"entity_group": entity["label"], "word": entity["text"]} for entity in entities]
