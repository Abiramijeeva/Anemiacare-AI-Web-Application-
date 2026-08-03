def indian_diet_plan(diagnosis):

    if "Iron" in diagnosis:
        return """
Iron Deficiency Diet (Indian):
• Palak (Spinach)
• Ragi
• Jaggery
• Dates
• Rajma
• Chana
• Pomegranate
• Beetroot
• Liver (if non-veg)
"""

    elif "Thalassemia" in diagnosis:
        return """
Thalassemia Diet:
• Avoid excess iron
• Green vegetables
• Dal
• Vitamin C rich fruits
"""

    else:
        return """
Balanced Indian Diet:
• Dal, Rice, Chapati
• Seasonal fruits
• Milk & Curd
• Dry fruits
"""