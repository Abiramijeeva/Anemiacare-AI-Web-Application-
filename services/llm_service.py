# services/llm_service.py
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ✅ FIXED: Secure API key loading (REMOVED HARDCODED KEY)
client = None
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    print("⚠️ WARNING: GROQ_API_KEY not found. Using fallback explanations.")

def generate_ai_explanation_split(hb, rbc, mcv, mch, mchc, rdw, age, diagnosis, severity):
    """Generate 5 detailed explanation sections"""
    prompt = f"""
    Patient: Age {age}, HB: {hb}g/dL, RBC: {rbc}, MCV: {mcv}fL
    Diagnosis: {diagnosis} ({severity} anemia)

    Explain the condition for a patient.

    IMPORTANT RULES:
    - Write ONLY bullet points
    - Each section must have 4-6 points
    - Each point must start with "- "
    - Keep sentences short and simple
    - No paragraphs

    FORMAT EXACTLY:

    WHAT:
    - point
    - point
    - point

    SYMPTOMS:
    - point
    - point
    - point

    RISKS:
    - point
    - point
    - point

    DIET:
    - point
    - point
    - point

    LIFESTYLE:
    - point
    - point
    - point
    """
    
    # ✅ IMPROVED FALLBACK - Condition-specific explanations
    fallback_responses = {
        "Iron Deficiency": {
            "what": "Iron Deficiency Anemia occurs when your body lacks sufficient iron to produce hemoglobin, the oxygen-carrying protein in red blood cells. Your hemoglobin level of {hb}g/dL is low, causing reduced oxygen delivery. This is the most common type of anemia worldwide, often due to poor dietary intake, blood loss, or absorption issues. It typically shows small red blood cells (low MCV) and is fully treatable with iron supplements and diet changes.",
            "symptoms": "Fatigue, weakness, pale skin, shortness of breath, dizziness, cold hands/feet, brittle nails, hair loss, and cravings for ice or non-food items (pica). These symptoms worsen gradually and impact daily activities like climbing stairs or concentrating at work. Women and children are particularly affected.",
            "risks": "Untreated iron deficiency can cause heart strain from working harder to pump oxygen-poor blood, developmental delays in children, and pregnancy complications. Chronic cases lead to organ stress and reduced quality of life. Early treatment prevents these serious outcomes.",
            "diet": "Eat palak paneer, ragi roti, jaggery, dates, beetroot, pomegranate, chickpeas, lentils daily. Include Vitamin C-rich amla, lemon, oranges with meals to boost iron absorption. Avoid tea/coffee with meals, calcium-rich foods simultaneously. Morning iron-rich breakfast works best.",
            "lifestyle": "Take iron supplements as prescribed (empty stomach), walk 30 mins daily, sleep 7-8 hours. Monitor Hb every 2 months, see hematologist if no improvement in 3 months. Space dairy 2 hours from iron-rich meals."
        },
        "Thalassemia": {
            "what": "Thalassemia is a genetic blood disorder reducing hemoglobin production, leading to ineffective red blood cell formation. Your blood shows characteristic microcytic anemia pattern. Unlike iron deficiency, iron supplements won't help and may harm. Requires specialized genetic management.",
            "symptoms": "Fatigue, jaundice, dark urine, bone deformities (severe cases), enlarged spleen, growth delays in children. Symptoms vary from mild (carrier) to transfusion-dependent severe forms.",
            "risks": "Iron overload from transfusions damages heart, liver, endocrine glands. Bone marrow expansion causes skeletal deformities. Regular monitoring and chelation therapy essential.",
            "diet": "Balanced diet, avoid iron supplements and iron-rich foods unnecessarily. Green leafy vegetables, dal, fruits okay in moderation. Focus on folate-rich foods: spinach, oranges, nuts. Consult hematologist before supplements.",
            "lifestyle": "Regular blood transfusions if severe, chelation therapy, annual heart/liver function tests. Genetic counseling for family planning. Avoid contact sports if splenomegaly present."
        }
    }
    
    try:
        if not client:
            raise Exception("No API client")
            
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1200
        )
        text = response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI Service Error: {e}")
        # Use condition-specific fallback
        fallback_key = None

        for key in fallback_responses:
            if key.lower() in diagnosis.lower():
                fallback_key = key
            break

        if not fallback_key:
            fallback_key = "Iron Deficiency"
        fallback_text = fallback_responses[fallback_key]
        fallback_text = {k: v.format(hb=hb) for k, v in fallback_text.items()}
        return fallback_text
    
    # Parse with better extraction
    parts = {
        'what': 'Your AI analysis shows specific blood patterns indicating this condition.',
        'symptoms': 'Common symptoms include fatigue and weakness. Consult your doctor.',
        'risks': 'Long-term monitoring and treatment recommended.',
        'diet': 'Follow iron-rich Indian diet with doctor guidance.',
        'lifestyle': 'Regular medical follow-up advised.'
    }
    
    lines = text.split('\n')
    current_key = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('WHAT:'):
            parts['what'] = line[5:].strip()
            current_key = 'what'
        elif line.startswith('SYMPTOMS:'):
            parts['symptoms'] = line[9:].strip()
            current_key = 'symptoms'
        elif line.startswith('RISKS:'):
            parts['risks'] = line[6:].strip()
            current_key = 'risks'
        elif line.startswith('DIET:'):
            parts['diet'] = line[5:].strip()
            current_key = 'diet'
        elif line.startswith('LIFESTYLE:'):
            parts['lifestyle'] = line[10:].strip()
            current_key = 'lifestyle'
        elif current_key and ':' not in line and line:
            parts[current_key] += ' ' + line
    
    # Limit length but keep more content (200 words)
    for key in parts:
        parts[key] = ' '.join(parts[key].split()[:200])
    
    return parts
