# vision_analyzer/Dockerfile

# Use the base image which has Python and core dependencies
FROM video-processing/base:latest

# Set the working directory
WORKDIR /home/app/vision_analyzer

# Copy the vision analyzer specific code
COPY . .

# Expose the port for the health check endpoint
EXPOSE 8003

# The command to run the Celery worker for this service.
# It listens for tasks on the 'vision_tasks' queue.
CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info", "-Q", "vision_tasks"]
