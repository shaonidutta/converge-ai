"""
Convert policy markdown documents to PDF
Requires: pip install markdown2 reportlab
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import markdown2
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
except ImportError:
    print("❌ Required packages not installed!")
    print("Please run: pip install markdown2 reportlab")
    sys.exit(1)

# Directories
DOCS_DIR = Path(__file__).parent.parent / "data" / "policy_documents"
PDF_DIR = Path(__file__).parent.parent / "docs" / "policies"
PDF_DIR.mkdir(parents=True, exist_ok=True)

# CSS for PDF styling
PDF_CSS = """
@page {
    size: A4;
    margin: 2.5cm 2cm;
    @top-center {
        content: "ConvergeAI - Policy Document";
        font-size: 10pt;
        color: #666;
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 10pt;
        color: #666;
    }
}

body {
    font-family: 'Arial', 'Helvetica', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    color: #2c3e50;
    font-size: 24pt;
    margin-top: 0;
    margin-bottom: 20pt;
    border-bottom: 3px solid #3498db;
    padding-bottom: 10pt;
}

h2 {
    color: #34495e;
    font-size: 18pt;
    margin-top: 20pt;
    margin-bottom: 12pt;
    border-bottom: 2px solid #ecf0f1;
    padding-bottom: 6pt;
}

h3 {
    color: #34495e;
    font-size: 14pt;
    margin-top: 16pt;
    margin-bottom: 10pt;
}

h4 {
    color: #555;
    font-size: 12pt;
    margin-top: 12pt;
    margin-bottom: 8pt;
}

p {
    margin-bottom: 10pt;
    text-align: justify;
}

ul, ol {
    margin-bottom: 10pt;
    padding-left: 20pt;
}

li {
    margin-bottom: 6pt;
}

strong {
    color: #2c3e50;
}

em {
    color: #555;
}

code {
    background-color: #f8f9fa;
    padding: 2pt 4pt;
    border-radius: 3pt;
    font-family: 'Courier New', monospace;
    font-size: 10pt;
}

pre {
    background-color: #f8f9fa;
    padding: 10pt;
    border-radius: 5pt;
    border-left: 4pt solid #3498db;
    overflow-x: auto;
    font-size: 10pt;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 15pt;
}

th {
    background-color: #3498db;
    color: white;
    padding: 8pt;
    text-align: left;
    font-weight: bold;
}

td {
    padding: 8pt;
    border-bottom: 1pt solid #ecf0f1;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

blockquote {
    border-left: 4pt solid #3498db;
    padding-left: 15pt;
    margin-left: 0;
    color: #555;
    font-style: italic;
}

hr {
    border: none;
    border-top: 2pt solid #ecf0f1;
    margin: 20pt 0;
}

.header-info {
    background-color: #ecf0f1;
    padding: 15pt;
    border-radius: 5pt;
    margin-bottom: 20pt;
}

.footer-info {
    background-color: #f8f9fa;
    padding: 15pt;
    border-radius: 5pt;
    margin-top: 20pt;
    font-size: 9pt;
    color: #666;
}
"""


def convert_markdown_to_pdf(md_file: Path, pdf_file: Path):
    """Convert a markdown file to PDF using reportlab"""
    try:
        # Read markdown content
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Create PDF
        doc = SimpleDocTemplate(
            str(pdf_file),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Container for PDF elements
        story = []

        # Define styles
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=20
        )

        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=16
        )

        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#555'),
            spaceAfter=8,
            spaceBefore=12
        )

        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY,
            spaceAfter=10
        )

        # Parse markdown and convert to PDF elements
        lines = md_content.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Title (# )
            if line.startswith('# '):
                text = line[2:].strip()
                story.append(Paragraph(text, title_style))
                story.append(Spacer(1, 12))

            # Heading 1 (## )
            elif line.startswith('## '):
                text = line[3:].strip()
                story.append(Paragraph(text, heading1_style))

            # Heading 2 (### )
            elif line.startswith('### '):
                text = line[4:].strip()
                story.append(Paragraph(text, heading2_style))

            # Heading 3 (#### )
            elif line.startswith('#### '):
                text = line[5:].strip()
                story.append(Paragraph(text, heading3_style))

            # Horizontal rule
            elif line.startswith('---'):
                story.append(Spacer(1, 12))

            # Bold text
            elif line.startswith('**') and line.endswith('**'):
                text = line[2:-2]
                story.append(Paragraph(f"<b>{text}</b>", body_style))

            # Regular paragraph
            else:
                # Handle bold and italic
                text = line
                text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)

                story.append(Paragraph(text, body_style))

            i += 1

        # Build PDF
        doc.build(story)

        return True
    except Exception as e:
        print(f"❌ Error converting {md_file.name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("=" * 80)
    print("CONVERTING POLICY DOCUMENTS TO PDF")
    print("=" * 80)
    print()
    
    # Find all markdown files
    md_files = sorted(DOCS_DIR.glob("*.md"))
    
    if not md_files:
        print("❌ No markdown files found in", DOCS_DIR)
        return
    
    print(f"Found {len(md_files)} markdown files")
    print()
    
    success_count = 0
    fail_count = 0
    
    for md_file in md_files:
        pdf_file = PDF_DIR / f"{md_file.stem}.pdf"
        print(f"Converting: {md_file.name} -> {pdf_file.name}")
        
        if convert_markdown_to_pdf(md_file, pdf_file):
            print(f"✅ Success: {pdf_file}")
            success_count += 1
        else:
            print(f"❌ Failed: {md_file.name}")
            fail_count += 1
        print()
    
    print("=" * 80)
    print("CONVERSION COMPLETE")
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📁 PDFs saved to: {PDF_DIR}")
    print("=" * 80)


if __name__ == "__main__":
    main()

