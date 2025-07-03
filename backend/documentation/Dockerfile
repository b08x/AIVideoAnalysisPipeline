# documentation/Dockerfile

# Use the base image
FROM video-processing/base:latest

# Install system dependencies required for PDF generation (e.g., via WeasyPrint)
# This might need adjustment based on the markdown-pdf library's underlying dependencies.
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libpango-1.0-0 \
#     libharfbuzz0b \
#     libharfbuzz-icu0 \
#     && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /home/app/documentation

# Copy the documentation service specific code
COPY . .

# Expose the port for the health check and download endpoints
EXPOSE 8004

# The command to run the Celery worker for this service.
# It listens for tasks on the 'doc_tasks' queue.
# We also run the FastAPI app using a different process manager or a script.
# For simplicity here, we'll just define the Celery command.
# A production setup might use gunicorn for FastAPI and a separate process for Celery.
CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info", "-Q", "doc_tasks"]

# To run both FastAPI and Celery in one container (for simplicity, not recommended for prod):
# CMD /bin/bash -c "uvicorn main:app --host 0.0.0.0 --port 8004 & celery -A tasks.celery_app worker --loglevel=info -Q doc_tasks"
