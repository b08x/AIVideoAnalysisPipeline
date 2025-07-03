# subtitle_processor/Dockerfile

# Use the base image which has Python and system dependencies
FROM video-processing/base:latest

# Set the working directory inside the container
WORKDIR /home/app/subtitle_processor

# Copy the subtitle processor specific code
COPY . .

# Expose the port for the health check endpoint
EXPOSE 8001

# The command to run the Celery worker for this service.
# It listens for tasks on the 'subtitle_tasks' queue.
CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info", "-Q", "subtitle_tasks"]
