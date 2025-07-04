# documentation/tasks.py
import os
from celery import Celery
from documentation.generator import ReportGenerator
from documentation.exporters import ReportExporter

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
celery_app = Celery("doc_tasks", broker=REDIS_URL, backend=REDIS_URL)

@celery_app.task(name="generate_report")
def generate_report(job_id: int, aggregated_data: dict):
    """
    A Celery task to generate the final report in multiple formats.
    """
    print(f"Job {job_id}: Starting report generation.")
    
    report_dir = f"/shared/{job_id}/reports"
    os.makedirs(report_dir, exist_ok=True)
    
    # 1. Generate Markdown report
    generator = ReportGenerator()
    markdown_content = generator.generate(job_id, aggregated_data)
    md_path = os.path.join(report_dir, "final_report.md")
    generator.save_report(markdown_content, md_path)

    # 2. Export to other formats (e.g., PDF)
    exporter = ReportExporter()
    pdf_path = os.path.join(report_dir, "final_report.pdf")
    try:
        exporter.to_pdf(md_path, pdf_path)
    except Exception as e:
        print(f"Job {job_id}: Could not generate PDF report. Error: {e}")

    # In a real system, you would update the job status in the database
    # and perhaps store the report paths.
    
    print(f"Job {job_id}: Report generation complete.")
    return {
        "status": "completed",
        "report_paths": {
            "markdown": md_path,
            "pdf": pdf_path if os.path.exists(pdf_path) else None
        }
    }

