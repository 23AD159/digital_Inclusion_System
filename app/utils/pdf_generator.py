import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

def generate_report_pdf(student_name, college, dept, year, score, category, badge, points, recommendations):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    story.append(Paragraph("Digital Inclusion & Workforce Readiness Report", styles['Title']))
    story.append(Spacer(1, 12))
    
    # Student details
    story.append(Paragraph(f"Student Detail: {student_name}", styles['Normal']))
    story.append(Paragraph(f"University ID & Location: {college}", styles['Normal']))
    story.append(Paragraph(f"Dept: {dept} | Batch: {year}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Scores and category
    story.append(Paragraph(f"Digital Readiness Meta-Score: {score} / 100", styles['Heading2']))
    story.append(Paragraph(f"Predicted Output Engine Category: {category}", styles['Normal']))
    story.append(Paragraph(f"Gamification Tier: {badge} | Points: {points}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Recommendations
    story.append(Paragraph("Dynamic Skill Gap Recommendations:", styles['Heading2']))
    for rec in recommendations:
        story.append(Paragraph(f"- {rec}", styles['Normal']))
        story.append(Spacer(1, 6))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
