from services.llm_service import generate_explanation

data = {
    "AGE": 35,
    "GENDER": 1,
    "HB": 8.5,
    "RBC": 3.8,
    "MCV": 72
}

print(generate_explanation(data, "Iron Deficiency", "Moderate"))
