# Multi-stage Dockerfile for AI Video Analysis Pipeline
# Optimized for size and build performance - RUNNING AS ROOT

# =============================================================================
# Stage 1: Base Dependencies
# Install system-level dependencies needed for both build and runtime
# =============================================================================
FROM linuxserver/ffmpeg:amd64-6.1.1 AS base-deps

# Install system dependencies in a single layer to minimize image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core system tools
    curl \
    ca-certificates \
    # Python runtime and minimal build tools
    python3 \
    python3-pip \
    python3-venv \
    # Graphics and OCR libraries (runtime dependencies)
    libxcb-glx0 \
    libxxf86vm-dev \
    libxcb-cursor0 \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# =============================================================================
# Stage 2: Python Build Environment
# Install build dependencies and compile Python packages
# =============================================================================
FROM base-deps AS python-builder

# Install build dependencies needed for compiling Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build tools for Python packages
    python3-dev \
    build-essential \
    gcc \
    g++ \
    # Additional build dependencies for ML packages
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Create virtual environment with uv
RUN uv venv /app/venv
ENV VIRTUAL_ENV=/app/venv
ENV PATH="/app/venv/bin:${PATH}"

# Copy requirements first for better layer caching
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN uv pip install --no-cache --requirement /tmp/requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# =============================================================================
# Stage 3: Runtime Environment
# Create minimal production image with only runtime dependencies
# =============================================================================
FROM base-deps AS runtime

WORKDIR /app

# Copy compiled virtual environment from builder stage
COPY --from=python-builder /app/venv /app/venv

# Copy application source code
COPY ./src ./

# Set up environment variables for Python virtual environment
ENV VIRTUAL_ENV=/app/venv
ENV PATH="/app/venv/bin:${PATH}"
ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV PYTHONUNBUFFERED=1

# Set default working directory
WORKDIR /app

# Reset the entrypoint from the base image to run our own command
ENTRYPOINT []

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
