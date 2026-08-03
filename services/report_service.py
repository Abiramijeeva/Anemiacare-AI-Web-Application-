from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Table

def generate_pdf(filename, data, anemia_type, severity, explanation):

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Anemia AI Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Anemia Type: {anemia_type}", styles["Normal"]))
    elements.append(Paragraph(f"Severity: {severity}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    table_data = [[k, str(v)] for k, v in data.items()]
    table = Table(table_data)
    elements.append(table)

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(explanation, styles["Normal"]))

    doc.build(elements)
