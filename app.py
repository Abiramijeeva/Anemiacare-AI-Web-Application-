import pandas as pd
from flask import Flask, render_template, request, send_file
import joblib
import os
import pytesseract
import pdfplumber
from PIL import Image
import re

from services.llm_service import generate_ai_explanation_split
from services.diet_service import indian_diet_plan
from services.risk_service import future_risk
from services.pdf_service import generate_hospital_report

app = Flask(__name__)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ==============================
# LOAD TRAINED MODELS (ONLY LOAD)
# ==============================

type_model = joblib.load("model/anemia_type_model.pkl")
severity_model = joblib.load("model/severity_model.pkl")
type_encoder = joblib.load("model/type_encoder.pkl")
severity_encoder = joblib.load("model/severity_encoder.pkl")

FEATURE_COLUMNS = [
    "HB", "RBC", "MCV", "MCH",
    "MCHC", "RDW",
    "AGE", "GENDER"
]

# =====================================================
# TEXT EXTRACTION
# =====================================================

def extract_values_from_text(text):

    text = text.replace(",", " ")
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    def find_value(keywords):
        for word in keywords:
            pattern = rf"{word}.*?(\d+\.?\d*)"
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                for num in matches:
                    value = float(num)
                    if 0 < value < 500:
                        return value
        return None

    return {
        "HB": find_value(["Hemoglobin", "Haemoglobin", "HGB", "Hb"]),
        "RBC": find_value(["RBC Count", "RBC", "R.B.C"]),
        "MCV": find_value(["MCV"]),
        "MCH": find_value(["MCH"]),
        "MCHC": find_value(["MCHC"]),
        "RDW": find_value(["RDW"])
    }

def extract_from_file(filepath):

    text = ""

    if filepath.lower().endswith(".pdf"):
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted
    else:
        img = Image.open(filepath)
        text = pytesseract.image_to_string(img)

    return extract_values_from_text(text)

# =====================================================
# COMMON PREDICTION FUNCTION
# =====================================================

def run_prediction(hb, rbc, mcv, mch, mchc, rdw, age, gender):

    features_df = pd.DataFrame([{
        "HB": hb,
        "RBC": rbc,
        "MCV": mcv,
        "MCH": mch,
        "MCHC": mchc,
        "RDW": rdw,
        "AGE": age,
        "GENDER": gender
    }])

    type_encoded = type_model.predict(features_df)[0]
    severity_encoded = severity_model.predict(features_df)[0]

    diagnosis = type_encoder.inverse_transform([type_encoded])[0]
    if "Normal" in diagnosis:
        diagnosis = "Normal"
    severity = severity_encoder.inverse_transform([severity_encoded])[0]

    confidence = round(
        max(type_model.predict_proba(features_df)[0]) * 100,
        2
    )

    return diagnosis, severity, confidence

# =====================================================
# ROUTES
# =====================================================

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/choose")
def choose():
    return render_template("choose.html")

@app.route("/manual")
def manual():
    return render_template("manual.html")

# =====================================================
# MANUAL ENTRY
# =====================================================

@app.route("/predict", methods=["POST"])
def predict():
    # Get form data
    data = {
        "HB": request.form.get("hb"),
        "RBC": request.form.get("rbc"),
        "MCV": request.form.get("mcv"),
        "MCH": request.form.get("mch"),
        "MCHC": request.form.get("mchc"),
        "RDW": request.form.get("rdw"),
        "AGE": request.form.get("age"),
        "GENDER": request.form.get("gender")
    }

    # Validation
    missing = [k for k, v in data.items() if not v]
    if missing:
        return render_template(
            "manual.html",
            message=f"Please enter missing values: {', '.join(missing)}"
        )

    # Convert to float
    hb = float(data["HB"])
    rbc = float(data["RBC"])
    mcv = float(data["MCV"])
    mch = float(data["MCH"])
    mchc = float(data["MCHC"])
    rdw = float(data["RDW"])
    age = float(data["AGE"])
    gender = 1 if data["GENDER"] == "Male" else 0

    # USE YOUR FUNCTION HERE 👇
    diagnosis, severity, confidence = run_prediction(hb, rbc, mcv, mch, mchc, rdw, age, gender)

    # Generate explanations (NEW split format)
    explanation_parts = generate_ai_explanation_split(hb, rbc, mcv, mch, mchc, rdw, age, diagnosis, severity)

    # AI insights
    diet = indian_diet_plan(diagnosis)
    risk = future_risk(hb, diagnosis)

    return render_template(
        "result.html",
        result=diagnosis,
        severity=severity,
        confidence=confidence,
        explanation_what=explanation_parts['what'],
        explanation_symptoms=explanation_parts['symptoms'],
        explanation_risks=explanation_parts['risks'],
        explanation_diet=explanation_parts['diet'],
        explanation_lifestyle=explanation_parts['lifestyle'],
        diet = diet,
        risk = risk, 
        hb=hb, rbc=rbc, mcv=mcv, mch=mch, mchc=mchc, rdw=rdw, age=age
    )

# =====================================================
# UPLOAD
# =====================================================

@app.route("/upload", methods=["GET", "POST"])
def upload():

    if request.method == "POST":

        # ===============================
        # CASE 1: USER FIXING MISSING VALUES
        # ===============================
        if request.form.get("manual_fix") == "1":

            hb = float(request.form.get("HB"))
            rbc = float(request.form.get("RBC"))
            mcv = float(request.form.get("MCV"))
            mch = float(request.form.get("MCH"))
            mchc = float(request.form.get("MCHC"))
            rdw = float(request.form.get("RDW"))
            age = float(request.form.get("age"))
            gender_val = 1 if request.form.get("gender") == "Male" else 0

            diagnosis, severity, confidence = run_prediction(
                hb, rbc, mcv, mch, mchc, rdw, age, gender_val
            )

            explanation_parts = generate_ai_explanation_split(
                hb, rbc, mcv, mch, mchc, rdw, age, diagnosis, severity
            )

            diet = indian_diet_plan(diagnosis)
            risk = future_risk(hb, diagnosis)

            return render_template(
                "result.html",
                result=diagnosis,
                severity=severity,
                confidence=confidence,
                explanation_what=explanation_parts['what'],
                explanation_symptoms=explanation_parts['symptoms'],
                explanation_risks=explanation_parts['risks'],
                explanation_diet=explanation_parts['diet'],
                explanation_lifestyle=explanation_parts['lifestyle'],
                diet=diet,
                risk=risk,
                hb=hb, rbc=rbc, mcv=mcv,
                mch=mch, mchc=mchc,
                rdw=rdw, age=age
            )

        # ===============================
        # CASE 2: INITIAL FILE UPLOAD
        # ===============================

        file = request.files.get("file")
        age = request.form.get("age")
        gender = request.form.get("gender")

        if not file or file.filename == "":
            return render_template("upload.html",
                                   message="Please select a file.")

        if not age or not gender:
            return render_template("upload.html",
                                   message="Please enter Age and Gender.")

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        values = extract_from_file(filepath)

        missing = [k for k, v in values.items() if v is None]

        if missing:
            return render_template(
                "upload.html",
                extracted=values,
                missing=missing,
                age=age,
                gender=gender,
                show_fix=True
            )

        hb = float(values["HB"])
        rbc = float(values["RBC"])
        mcv = float(values["MCV"])
        mch = float(values["MCH"])
        mchc = float(values["MCHC"])
        rdw = float(values["RDW"])
        age = float(age)
        gender_val = 1 if gender == "Male" else 0

        diagnosis, severity, confidence = run_prediction(
            hb, rbc, mcv, mch, mchc, rdw, age, gender_val
        )

        explanation_parts = generate_ai_explanation_split(
            hb, rbc, mcv, mch, mchc, rdw, age, diagnosis, severity
        )

        diet = indian_diet_plan(diagnosis)
        risk = future_risk(hb, diagnosis)

        return render_template(
            "result.html",
            result=diagnosis,
            severity=severity,
            confidence=confidence,
            explanation_what=explanation_parts['what'],
            explanation_symptoms=explanation_parts['symptoms'],
            explanation_risks=explanation_parts['risks'],
            explanation_diet=explanation_parts['diet'],
            explanation_lifestyle=explanation_parts['lifestyle'],
            diet=diet,
            risk=risk,
            hb=hb, rbc=rbc, mcv=mcv,
            mch=mch, mchc=mchc,
            rdw=rdw, age=age
        )

    return render_template("upload.html")

# =====================================================

@app.route("/download_report", methods=["POST"])
def download_report():

    # Get values from hidden form fields
    hb = float(request.form.get("hb"))
    rbc = float(request.form.get("rbc"))
    mcv = float(request.form.get("mcv"))
    mch = float(request.form.get("mch"))
    mchc = float(request.form.get("mchc"))
    rdw = float(request.form.get("rdw"))
    age = float(request.form.get("age"))
    gender = 1 if request.form.get("gender") == "Male" else 0

    # Run prediction again (SAFE + ACCURATE)
    diagnosis, severity, confidence = run_prediction(
        hb, rbc, mcv, mch, mchc, rdw, age, gender
    )

    # ✅ Get explanations from hidden form fields (NO AI REGENERATION)
    what = request.form.get("explanation_what")
    symptoms = request.form.get("explanation_symptoms")
    risks = request.form.get("explanation_risks")
    diet = request.form.get("explanation_diet")
    lifestyle = request.form.get("explanation_lifestyle")
    def format_bullets(text):
        points = [p.strip() for p in text.split("-") if p.strip()]
        return "\n".join([f"• {p}" for p in points])
    full_explanation = f"""
WHAT IS {diagnosis.upper()}?

{format_bullets(what)}

------------------------------------------------------------

SYMPTOMS:

{format_bullets(symptoms)}

------------------------------------------------------------

LONG-TERM RISKS:

{format_bullets(risks)}

------------------------------------------------------------

INDIAN DIET PLAN:

{format_bullets(diet)}

------------------------------------------------------------

LIFESTYLE ADVICE:

{format_bullets(lifestyle)}
"""

    filename = "anemia_report.pdf"

    patient_data = {
        "hb": hb,
        "rbc": rbc,
        "mcv": mcv,
        "mch": mch,
        "mchc": mchc,
        "rdw": rdw,
        "age": age,
        "gender": "Male" if gender == 1 else "Female"
    }

    generate_hospital_report(
        filename,
        patient_data,
        diagnosis,
        severity,
        confidence,
        full_explanation
    )

    return send_file(filename, as_attachment=True)
# =====================================================
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)