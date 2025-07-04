# documentation/exporters.py
import os
from markdown_pdf import MarkdownPdf, Section

class ReportExporter:
    """
    Exports a markdown file to other formats like PDF.
    """
    def to_pdf(self, markdown_path: str, output_path: str):
        """
        Converts a markdown file to a PDF.

        Args:
            markdown_path: The path to the source markdown file.
            output_path: The path to save the output PDF file.
        """
        if not os.path.exists(markdown_path):
            raise FileNotFoundError(f"Markdown file not found: {markdown_path}")

        print(f"Converting {markdown_path} to PDF at {output_path}")
        
        try:
            pdf = MarkdownPdf()
            with open(markdown_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pdf.add_section(Section(content))
            pdf.save(output_path)
            print(f"Successfully exported PDF to {output_path}")
        except Exception as e:
            print(f"Failed to export PDF: {e}")
            # Depending on requirements, you might want to raise the exception
            # raise e

