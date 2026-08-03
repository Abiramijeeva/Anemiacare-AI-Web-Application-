from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import  getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from datetime import datetime


def generate_hospital_report(filename, patient_data, diagnosis, severity, confidence, full_explanation):

    doc = SimpleDocTemplate(filename, pagesize=pagesizes.A4)
    elements = []

    styles = getSampleStyleSheet()

    # Custom Styles
    header_style = styles["Heading1"]
    header_style.alignment = 1  # Center

    normal_style = styles["Normal"]

    # ===== HOSPITAL HEADER =====
    elements.append(Paragraph("PERSONALIZED ANEMIA ASSESSMENT AND CARE PLAN", header_style))
    elements.append(Paragraph("Comprehensive Blood Analysis Report", styles["Heading3"]))
    elements.append(Spacer(1, 0.3 * inch))

    # ===== REPORT INFO =====
    report_id = f"ANM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    date_str = datetime.now().strftime("%d %B %Y")

    elements.append(Paragraph(f"<b>Report ID:</b> {report_id}", normal_style))
    elements.append(Paragraph(f"<b>Date:</b> {date_str}", normal_style))
    elements.append(Spacer(1, 0.3 * inch))

    # ===== PATIENT DATA TABLE =====
    data_table = [
        ["Parameter", "Value"],
        ["Hemoglobin (Hb)", patient_data["hb"]],
        ["RBC Count", patient_data["rbc"]],
        ["MCV", patient_data["mcv"]],
        ["MCH", patient_data["mch"]],
        ["MCHC", patient_data["mchc"]],
        ["RDW", patient_data["rdw"]],
        ["Age", patient_data["age"]],
        ["Gender", patient_data["gender"]],
    ]

    table = Table(data_table, colWidths=[3 * inch, 2 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.4 * inch))

    # ===== DIAGNOSIS SECTION =====
    elements.append(Paragraph("<b>DIAGNOSIS:</b>", styles["Heading2"]))
    elements.append(Paragraph(f"{diagnosis}", normal_style))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"<b>Severity Level:</b> {severity}", normal_style))
    elements.append(Paragraph(f"<b>Model Confidence:</b> {confidence}%", normal_style))
    elements.append(Spacer(1, 0.4 * inch))

    # ===== EXPLANATION =====
    elements.append(Paragraph("<b>Medical Explanation</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.3 * inch))

    sections = full_explanation.split("------------------------------------------------------------")

    for section in sections:

        section = section.strip()

        if ":" in section:
            title, content = section.split(":", 1)

            # Section Title
            elements.append(Paragraph(f"<b>{title.strip()}</b>", styles["Heading3"]))
            elements.append(Spacer(1, 0.15 * inch))

            # Section Content (wrap properly)
            for line in content.strip().split("\n"):
                elements.append(Paragraph(line.strip(), normal_style))
                elements.append(Spacer(1, 0.12 * inch))

            # Space before next section
            elements.append(Spacer(1, 0.35 * inch))
    

    doc.build(elements)