# video_processor/Dockerfile

# Use the base image which has Python, FFmpeg, and OpenCV
FROM video-processing/base:latest

# Set the working directory
WORKDIR /home/app/video_processor

# Copy the video processor specific code
COPY . .

# Expose the port for the health check endpoint
EXPOSE 8002

# The command to run the Celery worker for this service.
# It listens for tasks on the 'video_tasks' queue.
CMD ["celery", "-A", "tasks.celery_app", "worker", "--loglevel=info", "-Q", "video_tasks"]
