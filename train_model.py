

import pandas as pd
import joblib
import os
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder

# ==============================
# LOAD DATASET
# ==============================
df = pd.read_csv("BDCBC7196_Hematology_Dataset.csv")

# ==============================
# FILTER ONLY ANEMIA + NORMAL
# ==============================
anemia_classes = [
    "Iron Deficiency",
    "Microcytic Anemia",
    "Normocytic Anemia",
    "Anemia of Chronic Disease",
    "Normal"
]

df = df[df["Diagnosis"].isin(anemia_classes)]

# ==============================
# RENAME
# ==============================
df.rename(columns={
    "Gender": "GENDER",
    "Age": "AGE",
    "Hb": "HB",
    "Diagnosis": "TYPE"
}, inplace=True)

# ==============================
# CREATE SEVERITY FROM HB
# ==============================
def classify_severity(hb):
    if hb >= 12:
        return "Normal"
    elif 10 <= hb < 12:
        return "Mild"
    elif 7 <= hb < 10:
        return "Moderate"
    else:
        return "Severe"

df["SEVERITY"] = df["HB"].apply(classify_severity)

# ==============================
# FEATURES
# ==============================
features = [
    "HB", "RBC", "MCV", "MCH",
    "MCHC", "RDW",
    "AGE", "GENDER"
]

X = df[features]

# ==============================
# ENCODE TARGETS
# ==============================
type_encoder = LabelEncoder()
y_type = type_encoder.fit_transform(df["TYPE"])

severity_encoder = LabelEncoder()
y_severity = severity_encoder.fit_transform(df["SEVERITY"])

# ==============================
# TRAIN MODELS
# ==============================
type_model = XGBClassifier(n_estimators=300, random_state=42, use_label_encoder=False, eval_metric="mlogloss")
severity_model = XGBClassifier(n_estimators=200, random_state=42, use_label_encoder=False, eval_metric="mlogloss")

type_model.fit(X, y_type)
severity_model.fit(X, y_severity)

# ==============================
# SAVE MODELS
# ==============================
os.makedirs("model", exist_ok=True)

joblib.dump(type_model, "model/anemia_type_model.pkl")
joblib.dump(severity_model, "model/severity_model.pkl")
joblib.dump(type_encoder, "model/type_encoder.pkl")
joblib.dump(severity_encoder, "model/severity_encoder.pkl")

print("✅ Anemia models trained successfully!")


# import pandas as pd
# import joblib
# import os

# from xgboost import XGBClassifier
# from sklearn.preprocessing import LabelEncoder
# from sklearn.model_selection import train_test_split, cross_val_score
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

# from imblearn.over_sampling import SMOTE

# # ==============================
# # LOAD DATASET
# # ==============================
# df = pd.read_csv("BDCBC7196_Hematology_Dataset.csv")

# # Remove duplicates
# df = df.drop_duplicates()

# # ==============================
# # FILTER DATA
# # ==============================
# anemia_classes = [
#     "Iron Deficiency",
#     "Microcytic Anemia",
#     "Normocytic Anemia",
#     "Anemia of Chronic Disease",
#     "Normal"
# ]

# df = df[df["Diagnosis"].isin(anemia_classes)].copy()

# # ==============================
# # RENAME COLUMNS
# # ==============================
# df.rename(columns={
#     "Gender": "GENDER",
#     "Age": "AGE",
#     "Hb": "HB",
#     "Diagnosis": "TYPE"
# }, inplace=True)

# # ==============================
# # CREATE SEVERITY
# # ==============================
# def classify_severity(hb):
#     if hb >= 12:
#         return "Normal"
#     elif 10 <= hb < 12:
#         return "Mild"
#     elif 7 <= hb < 10:
#         return "Moderate"
#     else:
#         return "Severe"

# df["SEVERITY"] = df["HB"].apply(classify_severity)

# # ==============================
# # ENCODE GENDER
# # ==============================
# gender_encoder = LabelEncoder()
# df["GENDER"] = gender_encoder.fit_transform(df["GENDER"])

# # ==============================
# # FEATURES
# # ==============================

# # Type model (can use HB)
# features_type = [
#     "HB", "RBC", "MCV", "MCH",
#     "MCHC", "RDW",
#     "AGE", "GENDER"
# ]

# # Severity model (NO HB to avoid leakage)
# features_severity = [
#     "RBC", "MCV", "MCH",
#     "MCHC", "RDW",
#     "AGE", "GENDER"
# ]

# X_type = df[features_type]
# X_sev = df[features_severity]

# # ==============================
# # TARGET ENCODING
# # ==============================
# type_encoder = LabelEncoder()
# y_type = type_encoder.fit_transform(df["TYPE"])

# severity_encoder = LabelEncoder()
# y_severity = severity_encoder.fit_transform(df["SEVERITY"])

# # ==============================
# # TRAIN-TEST SPLIT
# # ==============================
# X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
#     X_type, y_type, test_size=0.2, random_state=42, stratify=y_type
# )

# X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
#     X_sev, y_severity, test_size=0.2, random_state=42, stratify=y_severity
# )

# # ==============================
# # HANDLE IMBALANCE (SMOTE)
# # ==============================
# smote = SMOTE(random_state=42)
# X_train_s, y_train_s = smote.fit_resample(X_train_s, y_train_s)

# # ==============================
# # MODELS
# # ==============================
# type_model = XGBClassifier(
#     n_estimators=300,
#     max_depth=5,
#     learning_rate=0.1,
#     random_state=42,
#     eval_metric="mlogloss"
# )

# severity_model = XGBClassifier(
#     n_estimators=300,
#     max_depth=5,
#     learning_rate=0.1,
#     random_state=42,
#     eval_metric="mlogloss"
# )

# # ==============================
# # TRAIN
# # ==============================
# type_model.fit(X_train_t, y_train_t)
# severity_model.fit(X_train_s, y_train_s)

# # ==============================
# # CROSS VALIDATION (TYPE MODEL)
# # ==============================
# cv_scores = cross_val_score(type_model, X_type, y_type, cv=5)
# print("\n📊 Cross Validation Accuracy (Type Model):", round(cv_scores.mean(), 4))

# # ==============================
# # PREDICTIONS
# # ==============================
# y_pred_t = type_model.predict(X_test_t)
# y_pred_s = severity_model.predict(X_test_s)

# # ==============================
# # METRICS FUNCTION
# # ==============================
# def print_metrics(y_true, y_pred, name):
#     print(f"\n📊 {name}")
#     print("Accuracy :", round(accuracy_score(y_true, y_pred), 4))
#     print("Precision:", round(precision_score(y_true, y_pred, average='weighted', zero_division=0), 4))
#     print("Recall   :", round(recall_score(y_true, y_pred, average='weighted'), 4))
#     print("F1 Score :", round(f1_score(y_true, y_pred, average='weighted'), 4))

# # ==============================
# # RESULTS
# # ==============================
# print_metrics(y_test_t, y_pred_t, "Anemia Type Model")
# print_metrics(y_test_s, y_pred_s, "Severity Model")

# # ==============================
# # CLASSIFICATION REPORT
# # ==============================
# print("\n🔍 Type Model Report:")
# print(classification_report(y_test_t, y_pred_t, target_names=type_encoder.classes_, zero_division=0))

# print("\n🔍 Severity Model Report:")
# print(classification_report(y_test_s, y_pred_s, target_names=severity_encoder.classes_, zero_division=0))

# # ==============================
# # SAVE MODELS
# # ==============================
# os.makedirs("model", exist_ok=True)

# joblib.dump(type_model, "model/anemia_type_model.pkl")
# joblib.dump(severity_model, "model/severity_model.pkl")
# joblib.dump(type_encoder, "model/type_encoder.pkl")
# joblib.dump(severity_encoder, "model/severity_encoder.pkl")
# joblib.dump(gender_encoder, "model/gender_encoder.pkl")

# print("\n✅ FINAL MODELS TRAINED & SAVED SUCCESSFULLY!")