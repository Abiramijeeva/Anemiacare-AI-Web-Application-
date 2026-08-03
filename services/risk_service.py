# def calculate_risk(severity, hb, age):
#     base = {
#         "Normal": 10,
#         "Mild": 40,
#         "Moderate": 70,
#         "Severe": 90
#     }

#     score = base.get(severity, 20)

#     if hb < 7:
#         score += 5

#     if age > 60:
#         score += 5

#     return min(score, 100)





def future_risk(hb, diagnosis):

    if hb < 7:
        return "Severe anemia may cause heart strain and organ stress."

    if "Leukemia" in diagnosis:
        return "Immediate hematologist consultation required."

    if "Polycythemia" in diagnosis:
        return "Risk of blood clots and stroke."

    return "No immediate severe risk detected."