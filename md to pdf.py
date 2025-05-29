import os
import glob
import markdown
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import re
from html import unescape


def convert_md_folder_to_single_pdf_reportlab(input_folder, output_pdf):
    """
    Convert all .md files in a folder to a single PDF using ReportLab
    """
    # Get all .md files in the directory
    md_files = glob.glob(os.path.join(input_folder, '*.md'))

    if not md_files:
        print(f"No .md files found in {input_folder}")
        return

    # Sort files alphabetically for consistent ordering
    md_files.sort()

    print(f"Found {len(md_files)} markdown files:")
    for file in md_files:
        print(f"  - {os.path.basename(file)}")

    # Create PDF document
    doc = SimpleDocTemplate(output_pdf, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    # Get styles
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=HexColor('#2c3e50'),
        borderWidth=2,
        borderColor=HexColor('#3498db'),
        borderPadding=10
    )

    filename_style = ParagraphStyle(
        'FilenameStyle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=20,
        textColor=HexColor('#e74c3c'),
        borderWidth=1,
        borderColor=HexColor('#e74c3c'),
        borderPadding=8
    )

    def clean_html_for_reportlab(html_text):
        """Clean HTML to work better with ReportLab"""
        # Remove unsupported tags but keep content
        html_text = re.sub(r'<code[^>]*>', '<font name="Courier">', html_text)
        html_text = re.sub(r'</code>', '</font>', html_text)
        html_text = re.sub(r'<pre[^>]*>', '<font name="Courier"><br/>', html_text)
        html_text = re.sub(r'</pre>', '</font><br/>', html_text)
        html_text = re.sub(r'<table[^>]*>.*?</table>', '[Table content - see original file]', html_text,
                           flags=re.DOTALL)
        html_text = re.sub(r'<[^>]+>', '', html_text)  # Remove remaining HTML tags
        html_text = unescape(html_text)  # Decode HTML entities
        return html_text

    for i, md_file in enumerate(md_files):
        print(f"Processing: {os.path.basename(md_file)}")

        try:
            # Read markdown file
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()

            # Add filename as header
            filename = os.path.basename(md_file)
            story.append(Paragraph(f"File: {filename}", filename_style))
            story.append(Spacer(1, 12))

            # Convert markdown to HTML first
            html_content = markdown.markdown(md_content)

            # Clean HTML for ReportLab
            clean_content = clean_html_for_reportlab(html_content)

            # Split content into paragraphs and add to story
            paragraphs = clean_content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # Detect headers (lines starting with multiple #)
                    if para.strip().startswith('# '):
                        story.append(Paragraph(para.strip()[2:], styles['Heading1']))
                    elif para.strip().startswith('## '):
                        story.append(Paragraph(para.strip()[3:], styles['Heading2']))
                    elif para.strip().startswith('### '):
                        story.append(Paragraph(para.strip()[4:], styles['Heading3']))
                    else:
                        story.append(Paragraph(para.strip(), styles['Normal']))
                    story.append(Spacer(1, 12))

            # Add page break after each file except the last one
            if i < len(md_files) - 1:
                story.append(PageBreak())

        except Exception as e:
            print(f"Error processing {md_file}: {e}")
            story.append(Paragraph(f"Error processing {os.path.basename(md_file)}: {str(e)}", styles['Normal']))
            continue

    try:
        # Build PDF
        doc.build(story)
        print(f"\nSuccessfully created PDF: {output_pdf}")
        print(f"Total files processed: {len(md_files)}")

    except Exception as e:
        print(f"Error creating PDF: {e}")


# Alternative method using markdown2pdf (simpler but requires wkhtmltopdf)
def convert_using_markdown2pdf(input_folder, output_pdf):
    """
    Alternative method using markdown2pdf package
    Requires: pip install markdown2pdf
    And wkhtmltopdf installed on system
    """
    try:
        import markdown2pdf

        md_files = glob.glob(os.path.join(input_folder, '*.md'))
        md_files.sort()

        if not md_files:
            print(f"No .md files found in {input_folder}")
            return

        print(f"Found {len(md_files)} markdown files")

        # Combine all markdown files
        combined_md = ""
        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                filename = os.path.basename(md_file)
                combined_md += f"\n\n# {filename}\n\n"
                combined_md += f.read()
                combined_md += "\n\n---\n\n"  # Page break in markdown

        # Write combined markdown to temp file
        temp_md = "temp_combined.md"
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(combined_md)

        # Convert to PDF
        markdown2pdf.convert(temp_md, output_pdf)

        # Clean up temp file
        os.remove(temp_md)

        print(f"Successfully created PDF: {output_pdf}")

    except ImportError:
        print("markdown2pdf not installed. Install with: pip install markdown2pdf")
    except Exception as e:
        print(f"Error with markdown2pdf: {e}")


# Usage
if __name__ == "__main__":
    input_folder = "crud_docs/"
    output_pdf = "crud_documentation.pdf"

    # Check if input folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' does not exist!")
    else:
        print("Choose conversion method:")
        print("1. ReportLab (recommended - no external dependencies)")
        print("2. markdown2pdf (requires wkhtmltopdf)")

        choice = input("Enter choice (1 or 2), or press Enter for default (1): ").strip()

        if choice == "2":
            convert_using_markdown2pdf(input_folder, output_pdf)
        else:
            # Install reportlab if not already installed
            try:
                import reportlab

                convert_md_folder_to_single_pdf_reportlab(input_folder, output_pdf)
            except ImportError:
                print("ReportLab not installed. Install with: pip install reportlab")
                print("Then run the script again.")