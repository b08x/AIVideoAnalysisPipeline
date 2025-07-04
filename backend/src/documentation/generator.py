# documentation/generator.py
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

class ReportGenerator:
    """
    Generates a markdown report from analysis data using Jinja2 templates.
    """
    def __init__(self, template_dir: str = "documentation/templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template("report_template.md")

    def generate(self, job_id: int, aggregated_data: dict) -> str:
        """
        Renders the report template with the provided data.

        Args:
            job_id: The ID of the processing job.
            aggregated_data: A dictionary containing all the analysis results
                             (utterances, topics, visual_analyses, etc.).

        Returns:
            A string containing the rendered markdown report.
        """
        # Prepare a summary for the report header
        summary_data = {
            "duration_seconds": aggregated_data.get("video_metadata", {}).get("duration_seconds", 0),
            "total_utterances": len(aggregated_data.get("utterances", [])),
            "total_topics": len(aggregated_data.get("topics", [])),
            "total_frames_analyzed": len(aggregated_data.get("visual_analyses", [])),
        }

        render_context = {
            "job_id": job_id,
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": summary_data,
            **aggregated_data
        }
        
        return self.template.render(render_context)

    def save_report(self, report_content: str, output_path: str):
        """
        Saves the generated report content to a file.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        print(f"Report saved to {output_path}")

