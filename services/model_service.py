
import joblib
import pandas as pd

# ==============================
# LOAD MODELS
# ==============================
type_model = joblib.load("model/anemia_type_model.pkl")
severity_model = joblib.load("model/severity_model.pkl")
type_encoder = joblib.load("model/type_encoder.pkl")
severity_encoder = joblib.load("model/severity_encoder.pkl")

# ==============================
# FEATURES USED IN TRAINING
# ==============================
FEATURES = [
    "HB", "RBC", "MCV", "MCH",
    "MCHC", "RDW",
    "AGE", "GENDER"
]

# ==============================
# PREDICTION FUNCTION
# ==============================
def predict(input_data: dict):
    """
    input_data must contain:
    HB, RBC, MCV, MCH, MCHC, RDW, AGE, GENDER
    """

    # Convert to DataFrame
    df = pd.DataFrame([input_data])
    df = df[FEATURES]

    # ==========================
    # Predict Anemia Type
    # ==========================
    type_pred = type_model.predict(df)
    type_proba = type_model.predict_proba(df)

    anemia_type = type_encoder.inverse_transform(type_pred)[0]
    type_confidence = float(max(type_proba[0]))

    # ==========================
    # Predict Severity
    # ==========================
    severity_pred = severity_model.predict(df)
    severity_proba = severity_model.predict_proba(df)

    severity = severity_encoder.inverse_transform(severity_pred)[0]
    severity_confidence = float(max(severity_proba[0]))

    # ==========================
    # Return 4 values
    # ==========================
    return anemia_type, severity, type_confidence, severity_confidence
