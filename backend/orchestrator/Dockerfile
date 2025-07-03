# orchestrator/Dockerfile

# Use the base image with all system dependencies
FROM video-processing/base:latest

# Install python-multipart specifically for this service as root
USER root
RUN pip install python-multipart
USER app

# Set the working directory
WORKDIR /home/app/orchestrator

# Copy the orchestrator-specific code
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application using uvicorn
# The host 0.0.0.0 makes it accessible from outside the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
