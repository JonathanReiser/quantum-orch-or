"""
build_pdf.py — Generates a professional academic PDF version of full_quantum_governance_paper.md
"""

import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf(md_file="full_quantum_governance_paper.md", pdf_file="full_quantum_governance_paper.pdf"):
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1e293b"),
        alignment=1, # Center
        spaceAfter=12
    )

    author_style = ParagraphStyle(
        'AuthorStyle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#475569"),
        alignment=1, # Center
        spaceAfter=18
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Code'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#0284c7"),
        backColor=colors.HexColor("#f1f5f9"),
        borderColor=colors.HexColor("#cbd5e1"),
        borderWidth=0.5,
        borderPadding=6,
        spaceAfter=8
    )

    story = []

    if not os.path.exists(md_file):
        raise FileNotFoundError(f"{md_file} not found.")

    with open(md_file, "r") as f:
        lines = f.readlines()

    title_lines = []
    in_title = True

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        if stripped.startswith("# "):
            title_text = stripped[2:].replace("*", "")
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 6))
        elif stripped.startswith("**Author:**") or stripped.startswith("**Email:**") or stripped.startswith("**CERN") or stripped.startswith("**PyPI") or stripped.startswith("**GitHub"):
            clean_meta = stripped.replace("**", "").replace("[", "").replace("]", "").replace("`", "")
            story.append(Paragraph(clean_meta, author_style))
        elif stripped.startswith("## "):
            story.append(Spacer(1, 10))
            story.append(Paragraph(stripped[3:], h1_style))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))
        elif stripped.startswith("### "):
            story.append(Paragraph(stripped[4:], h1_style))
        elif stripped.startswith("```"):
            continue
        elif stripped.startswith("|"):
            clean_table = stripped.replace("|", "  ")
            story.append(Paragraph(f"<font color='#0284c7'>{clean_table}</font>", code_style))
        else:
            clean_para = stripped.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
            clean_para = clean_para.replace("&amp;lt;", "&lt;").replace("&amp;gt;", "&gt;")
            story.append(Paragraph(clean_para, body_style))

    doc.build(story)
    print(f"📄 Successfully generated PDF: {pdf_file}")

    desktop_path = os.path.expanduser("~/Desktop/full_quantum_governance_paper.pdf")
    shutil.copy(pdf_file, desktop_path)
    print(f"🖥️ Copied PDF to Mac Desktop: {desktop_path}")

    return pdf_file

if __name__ == "__main__":
    generate_pdf()
