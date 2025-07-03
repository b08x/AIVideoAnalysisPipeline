# backend/base/Dockerfile
# This Dockerfile creates a base image with all common system and Python dependencies
# required by the various backend services to ensure consistency and faster builds.

# Start from a lean Python 3.11 image
FROM python:3.11-slim

# Set environment variables to prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install essential system dependencies required for video/image processing and OCR
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # FFmpeg for video and audio manipulation
    ffmpeg \
    # OpenCV for computer vision tasks
    libopencv-dev \
    # Tesseract for Optical Character Recognition (OCR)
    tesseract-ocr \
    libtesseract-dev \
    # Git and curl for fetching dependencies if needed
    git \
    curl \
    # Build tools
    build-essential \
    && \
    # Clean up apt cache to keep the image size down
    rm -rf /var/lib/apt/lists/*

# --- Use uv for faster package installation ---

# First, upgrade pip and install uv
RUN pip install --upgrade pip
RUN pip install uv

# Copy the requirements file into the image
COPY requirements.txt .

# Install all Python dependencies using uv
# uv is a much faster alternative to pip
# The --no-cache flag is equivalent to pip's --no-cache-dir
# Use both PyPI and PyTorch CPU index for all packages
RUN uv pip install -r requirements.txt --no-cache --system --extra-index-url https://download.pytorch.org/whl/cpu

# --- User and directory setup ---

# Create a non-root user for security best practices
# Running applications as a non-root user minimizes potential security risks
RUN groupadd -r app && useradd --no-log-init -r -g app -d /home/app app
RUN mkdir -p /home/app && chown -R app:app /home/app

# Set the working directory for subsequent commands
WORKDIR /home/app

# Switch to the non-root user
USER app
