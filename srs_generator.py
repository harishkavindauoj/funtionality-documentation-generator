import os
import glob
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-1.5-flash")
PROJECT_NAME = os.getenv("PROJECT_NAME", "CRUD Application System")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Your Company Name")

genai.configure(api_key=GEMINI_API_KEY)


class SRSGenerator:
    def __init__(self, docs_dir="crud_docs", output_file="SRS_Document.pdf"):
        self.docs_dir = docs_dir
        self.output_file = output_file
        self.model = genai.GenerativeModel(MODEL_NAME)
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()

    def setup_custom_styles(self):
        """Setup custom paragraph styles for the document."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )

        # Heading styles
        self.heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        )

        self.heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=15,
            textColor=colors.darkgreen
        )

        # Body text style
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=6,
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0
        )

        # Code style
        self.code_style = ParagraphStyle(
            'CodeStyle',
            parent=self.styles['Code'],
            fontSize=9,
            spaceAfter=6,
            leftIndent=20,
            backgroundColor=colors.lightgrey
        )

    def load_prompt_template(self):
        """Load the SRS prompt template."""
        try:
            with open("srs_prompt_template.txt", "r", encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print("Warning: srs_prompt_template.txt not found. Using default prompt.")
            return self.get_default_prompt()

    def get_default_prompt(self):
        """Default prompt for SRS generation."""
        return """
        Analyze the following CRUD function documentation and create a comprehensive Software Requirements Specification (SRS) section.

        Function Documentation:
        {function_docs}

        Please provide:
        1. **Functional Requirements**: Clear, testable requirements in "The system shall..." format
        2. **Business Logic**: Explanation of the business rules and logic
        3. **Input/Output Specifications**: Detailed parameter descriptions and return values
        4. **Error Handling**: Expected error conditions and responses
        5. **Performance Requirements**: Any performance considerations
        6. **Security Considerations**: Authentication, authorization, data validation needs

        Write in professional SRS format suitable for stakeholders, developers, and testers.
        Use clear, non-technical language where possible while maintaining technical accuracy.
        """

    def read_documentation_files(self):
        """Read all generated documentation files."""
        doc_files = glob.glob(os.path.join(self.docs_dir, "*.md"))

        if not doc_files:
            raise FileNotFoundError(f"No documentation files found in {self.docs_dir}")

        documentation = {}
        for doc_file in doc_files:
            module_name = os.path.basename(doc_file).replace("_doc.md", "")
            try:
                with open(doc_file, "r", encoding='utf-8') as f:
                    documentation[module_name] = f.read()
                print(f"Loaded documentation for: {module_name}")
            except Exception as e:
                print(f"Error reading {doc_file}: {str(e)}")

        return documentation

    def generate_srs_content(self, function_docs):
        """Generate SRS content using Gemini AI."""
        prompt_template = self.load_prompt_template()
        prompt = prompt_template.format(function_docs=function_docs)

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating SRS content: {str(e)}")
            return f"Error generating content for this module: {str(e)}"

    def create_title_page(self, story):
        """Create the title page of the SRS document."""
        story.append(Spacer(1, 2 * inch))

        title = Paragraph(f"Software Requirements Specification", self.title_style)
        story.append(title)
        story.append(Spacer(1, 0.5 * inch))

        subtitle = Paragraph(f"{PROJECT_NAME}", self.heading1_style)
        story.append(subtitle)
        story.append(Spacer(1, 1 * inch))

        # Document info table
        doc_info = [
            ['Document Version:', '1.0'],
            ['Date:', datetime.now().strftime("%B %d, %Y")],
            ['Company:', COMPANY_NAME],
            ['Document Type:', 'Software Requirements Specification'],
            ['Status:', 'Draft']
        ]

        table = Table(doc_info, colWidths=[2 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))

        story.append(table)
        story.append(PageBreak())

    def create_table_of_contents(self, story, modules):
        """Create table of contents."""
        story.append(Paragraph("Table of Contents", self.heading1_style))
        story.append(Spacer(1, 0.2 * inch))

        toc_data = [
            ['Section', 'Page'],
            ['1. Introduction', '3'],
            ['2. System Overview', '4'],
            ['3. Functional Requirements', '5']
        ]

        page_num = 6
        for i, module in enumerate(modules, 4):
            toc_data.append([f'{i}. {module.title()} Module Requirements', str(page_num)])
            page_num += 2

        toc_data.extend([
            [f'{len(modules) + 4}. Non-Functional Requirements', str(page_num)],
            [f'{len(modules) + 5}. Appendices', str(page_num + 1)]
        ])

        toc_table = Table(toc_data, colWidths=[4 * inch, 1 * inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))

        story.append(toc_table)
        story.append(PageBreak())

    def create_introduction(self, story):
        """Create introduction section."""
        story.append(Paragraph("1. Introduction", self.heading1_style))

        intro_text = f"""
        This Software Requirements Specification (SRS) document describes the functional and 
        non-functional requirements for the {PROJECT_NAME}. This document serves as the 
        foundation for system design, development, testing, and maintenance activities.

        The system provides comprehensive CRUD (Create, Read, Update, Delete) operations 
        for managing various data entities within the application domain.
        """

        story.append(Paragraph(intro_text, self.body_style))
        story.append(Spacer(1, 0.2 * inch))

        story.append(Paragraph("1.1 Purpose", self.heading2_style))
        purpose_text = """
        The purpose of this document is to provide a detailed description of the requirements 
        for the CRUD application system, including functional requirements, interface 
        requirements, performance requirements, and other non-functional requirements.
        """
        story.append(Paragraph(purpose_text, self.body_style))

        story.append(Paragraph("1.2 Scope", self.heading2_style))
        scope_text = """
        This SRS covers all functional modules of the CRUD application system, including 
        data management operations, business logic implementation, error handling, and 
        security considerations.
        """
        story.append(Paragraph(scope_text, self.body_style))
        story.append(PageBreak())

    def create_system_overview(self, story):
        """Create system overview section."""
        story.append(Paragraph("2. System Overview", self.heading1_style))

        overview_text = f"""
        The {PROJECT_NAME} is designed to provide robust data management capabilities 
        through a well-structured CRUD interface. The system ensures data integrity, 
        implements proper error handling, and maintains security standards throughout 
        all operations.
        """

        story.append(Paragraph(overview_text, self.body_style))
        story.append(PageBreak())

    def add_module_requirements(self, story, module_name, srs_content):
        """Add requirements for a specific module."""
        story.append(Paragraph(f"{module_name.title()} Module Requirements", self.heading1_style))

        # Split the SRS content into paragraphs and format them
        paragraphs = srs_content.split('\n\n')

        for paragraph in paragraphs:
            if paragraph.strip():
                # Check if it's a heading (starts with **)
                if paragraph.strip().startswith('**') and paragraph.strip().endswith('**'):
                    heading_text = paragraph.strip().replace('**', '')
                    story.append(Paragraph(heading_text, self.heading2_style))
                elif paragraph.strip().startswith('*'):
                    # Handle bullet points
                    story.append(Paragraph(paragraph.strip(), self.body_style))
                else:
                    story.append(Paragraph(paragraph.strip(), self.body_style))

                story.append(Spacer(1, 0.1 * inch))

        story.append(PageBreak())

    def create_non_functional_requirements(self, story):
        """Create non-functional requirements section."""
        story.append(Paragraph("Non-Functional Requirements", self.heading1_style))

        nfr_content = """
        <b>Performance Requirements:</b><br/>
        • Response time for CRUD operations should not exceed 2 seconds under normal load<br/>
        • System should handle concurrent users efficiently<br/>
        • Database queries should be optimized for performance<br/><br/>

        <b>Security Requirements:</b><br/>
        • All input data must be validated and sanitized<br/>
        • Authentication required for all CRUD operations<br/>
        • Audit trail for all data modifications<br/>
        • Data encryption for sensitive information<br/><br/>

        <b>Reliability Requirements:</b><br/>
        • System availability should be 99.9%<br/>
        • Proper error handling and recovery mechanisms<br/>
        • Data backup and recovery procedures<br/><br/>

        <b>Usability Requirements:</b><br/>
        • Intuitive user interface design<br/>
        • Clear error messages and user feedback<br/>
        • Comprehensive user documentation<br/>
        """

        story.append(Paragraph(nfr_content, self.body_style))

    def generate_srs_document(self):
        """Generate the complete SRS document."""
        print("Starting SRS document generation...")

        # Read documentation files
        try:
            documentation = self.read_documentation_files()
        except FileNotFoundError as e:
            print(f"Error: {e}")
            return False

        # Create PDF document
        doc = SimpleDocTemplate(
            self.output_file,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )

        story = []

        # Create title page
        self.create_title_page(story)

        # Create table of contents
        self.create_table_of_contents(story, list(documentation.keys()))

        # Create introduction
        self.create_introduction(story)

        # Create system overview
        self.create_system_overview(story)

        # Add functional requirements section
        story.append(Paragraph("3. Functional Requirements", self.heading1_style))
        story.append(Paragraph(
            "The following sections detail the functional requirements for each module "
            "of the system, derived from the analysis of CRUD operations and business logic.",
            self.body_style
        ))
        story.append(PageBreak())

        # Process each module
        for module_name, module_docs in documentation.items():
            print(f"Processing module: {module_name}")

            # Generate SRS content for this module
            srs_content = self.generate_srs_content(module_docs)

            # Add to document
            self.add_module_requirements(story, module_name, srs_content)

        # Add non-functional requirements
        self.create_non_functional_requirements(story)

        # Build PDF
        try:
            doc.build(story)
            print(f"SRS document generated successfully: {self.output_file}")
            return True
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return False


def main():
    """Main function to run the SRS generator."""
    print("=== SRS Document Generator ===")

    # Configuration
    docs_dir = input("Enter documentation directory (default: crud_docs): ").strip() or "crud_docs"
    output_file = input("Enter output PDF filename (default: SRS_Document.pdf): ").strip() or "SRS_Document.pdf"

    # Create generator and run
    generator = SRSGenerator(docs_dir, output_file)

    if generator.generate_srs_document():
        print(f"\n SRS document created successfully!")
        print(f" File location: {os.path.abspath(output_file)}")
    else:
        print("\n Failed to generate SRS document. Check the errors above.")


if __name__ == "__main__":
    main()