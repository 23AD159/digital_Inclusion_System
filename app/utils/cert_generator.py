import io
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch

def generate_certificate_pdf(student_name, college, score, category, skills):
    """
    Generates a high-quality, professional certificate for workforce readiness.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), 
                            topMargin=0.5*inch, bottomMargin=0.5*inch,
                            leftMargin=0.5*inch, rightMargin=0.5*inch)
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    cert_title = ParagraphStyle(
        'CertTitle',
        parent=styles['Title'],
        fontSize=34,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=30,
        fontName='Helvetica-Bold'
    )
    
    sub_title = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.HexColor("#64748b"),
        alignment=1, # Center
        spaceAfter=20
    )

    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Normal'],
        fontSize=28,
        textColor=colors.HexColor("#4f46e5"),
        alignment=1,
        fontName='Helvetica-Bold',
        spaceAfter=20
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor("#334155"),
        alignment=1,
        leading=20
    )

    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#94a3b8"),
        alignment=1
    )

    story = []
    
    # 1. Header/Logo Placeholder
    story.append(Spacer(1, 40))
    story.append(Paragraph("CERTIFICATE OF ACHIEVEMENT", cert_title))
    
    # 2. Subtitle
    story.append(Paragraph("This is to certify that", sub_title))
    
    # 3. Student Name
    story.append(Paragraph(student_name, name_style))
    
    # 4. Success Body
    cert_id = str(uuid.uuid4())[:8].upper()
    date_str = datetime.now().strftime("%B %d, %Y")
    
    text = (
        f"has successfully completed the <b>Digital Workforce Readiness Assessment</b> with a verified "
        f"Industry Score of <b>{score}/100</b>. Based on our AI-Driven Multi-Layer Analysis, "
        f"the candidate is classified as <b>'{category}'</b>.<br/><br/>"
        f"<b>Verified Competencies:</b> {', '.join(skills) if skills else 'Systematic Problem Solving, Digital Literacy'}"
    )
    story.append(Paragraph(text, body_style))
    
    story.append(Spacer(1, 60))
    
    # 5. Signatures Table
    sig_data = [
        [Paragraph("__________________________", footer_style), "", Paragraph("__________________________", footer_style)],
        [Paragraph("<b>DigiGuide AI Engine</b>", footer_style), "", Paragraph("<b>Academic Verification Unit</b>", footer_style)],
    ]
    sig_table = Table(sig_data, colWidths=[3*inch, 2*inch, 3*inch])
    story.append(sig_table)
    
    story.append(Spacer(1, 40))
    
    # 6. Verification Footer
    v_text = f"Verification ID: D-INC-{cert_id} | Issued Date: {date_str} | Verified at Digital Inclusion Portal"
    story.append(Paragraph(v_text, footer_style))
    
    # Build
    doc.build(story)
    
    buffer.seek(0)
    return buffer
