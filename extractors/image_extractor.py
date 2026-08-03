import pytesseract
from PIL import Image
import re

def extract_from_image(filepath):

    img = Image.open(filepath)
    text = pytesseract.image_to_string(img)

    patterns = {
        "HB": r"(?:HB|Hemoglobin)\s*[:\-]?\s*(\d+\.?\d*)",
        "RBC": r"(?:RBC)\s*[:\-]?\s*(\d+\.?\d*)",
        "MCV": r"(?:MCV)\s*[:\-]?\s*(\d+\.?\d*)",
        "MCH": r"(?:MCH)\s*[:\-]?\s*(\d+\.?\d*)",
        "MCHC": r"(?:MCHC)\s*[:\-]?\s*(\d+\.?\d*)",
        "RDW": r"(?:RDW)\s*[:\-]?\s*(\d+\.?\d*)"
    }

    data = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = float(match.group(1))

    return data
