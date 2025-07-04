# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Video Analysis Pipeline - A full-stack application that analyzes videos using AI models. The system processes videos with subtitle files through a distributed backend pipeline and presents results via a React frontend. The architecture supports multiple AI models, real-time processing updates, and comprehensive video analysis including subtitle parsing, summarization, topic modeling, frame extraction, visual analysis, and report generation.

## Commands

### Quick Development

- `make up-dev` - Start development environment (shortcut for docker-compose)
- `make down-dev` - Stop development environment
- `make logs-dev` - View development logs
- `make build-dev` - Build development services only

### Frontend Development

- `cd frontend && npm install` - Install frontend dependencies
- `cd frontend && npm run dev` - Start frontend development server (Vite)
- `cd frontend && npm run build` - Build frontend for production
- `cd frontend && npm run preview` - Preview production build
- `cd frontend && npm run analyze` - Analyze bundle size

### Backend Development

- `docker-compose -f docker-compose.dev.yml up --build` - Start all backend services
- `docker-compose -f docker-compose.dev.yml down` - Stop all backend services
- `docker-compose -f docker-compose.dev.yml logs -f [service]` - View logs for specific service
- `docker-compose -f docker-compose.dev.yml exec orchestrator bash` - Access orchestrator shell

### Production Deployment

- `make build-prod` - Build production services with cache optimization
- `make up-prod` - Start production environment with Nginx
- `make down-prod` - Stop production environment
- `make logs-prod` - View production logs
- `make analyze-image` - Analyze Docker image size and layers

### Maintenance & Debugging

- `make clean` - Stop containers and remove volumes
- `make clean-all` - Complete cleanup including images
- `make help` - Show all available Makefile commands

### Environment Setup

- Backend: Copy `backend/.env.template` to `backend/.env` and configure API keys
- Frontend: Copy `frontend/.env.local.example` to `frontend/.env.local`
- Required API keys: `OPENROUTER_API_KEY`, `GEMINI_API_KEY`

### Environment Variables

**Backend (.env)**:
```
OPENROUTER_API_KEY="your_openrouter_api_key_for_claude_etc"
GEMINI_API_KEY="your_gemini_api_key_for_vision"
DATABASE_URL="postgresql://dev_user:dev_password@postgres:5432/video_processing"
REDIS_URL="redis://redis:6379/0"
STORAGE_ENDPOINT="http://minio:9000"
MINIO_ROOT_USER="minioadmin"
MINIO_ROOT_PASSWORD="minioadmin123"
CORS_ORIGINS="http://localhost:3000,http://localhost:5173"
```

**Frontend (.env.local)**:
```
GEMINI_API_KEY="your_gemini_api_key_here"
VITE_APP_API_URL="http://localhost:8000"
VITE_APP_WS_URL="ws://localhost:8000"
VITE_APP_USE_BACKEND=true
```

## Architecture

### System Architecture

The application uses a distributed microservices architecture with the following components:

**Backend Services (Docker Compose):**

- **Orchestrator Service** (FastAPI, port 8000): Main API gateway handling job management, file uploads, and WebSocket connections
- **4 Celery Workers**: Distributed processing for subtitle analysis, video processing, vision analysis, and documentation generation
- **PostgreSQL**: Job metadata and results storage
- **Redis**: Message broker for Celery task queue
- **MinIO**: S3-compatible object storage for files and reports

**Frontend (React + Vite):**

- Single-page application with real-time progress tracking
- TypeScript-based with comprehensive type definitions
- WebSocket integration for live processing updates

### Processing Pipeline

The backend implements a 7-stage asynchronous pipeline:

1. **Subtitle Processing**: Parses VTT/SRT/ASS formats, generates AI summaries, performs topic modeling using sentence-transformers + K-Means clustering
2. **Video Segmentation**: Validates video files and segments based on topic boundaries
3. **Frame Extraction**: Uses OpenCV for keyframe extraction with histogram-based scene change detection
4. **Visual Analysis**: Analyzes frames with Gemini Vision API, performs OCR with EasyOCR
5. **Report Generation**: Creates Markdown and PDF reports using Jinja2 templates

### Key Frontend Components

- `App.tsx` - Main application with two-stage UI (landing/processing) and state management
- `types.ts` - Complete TypeScript interfaces for all data structures
- `services/apiService.ts` - API communication layer with upload progress and WebSocket handling
- `components/` - Reusable UI components (file uploaders, progress indicators, modals)
- `utils/` - Validation, error handling, and feature flag utilities

### AI Integration

The system supports multiple AI models through OpenRouter and direct APIs:

- **Text Analysis**: OpenAI models for summarization and topic naming
- **Vision Analysis**: Google Gemini Pro Vision for frame description
- **Embeddings**: sentence-transformers for semantic clustering
- **Configurable Parameters**: Temperature, topP, topK for all models

### Data Flow

1. Frontend uploads video/subtitle files to MinIO via orchestrator
2. Orchestrator creates job record in PostgreSQL and dispatches Celery tasks
3. Workers process files asynchronously, updating job status in real-time
4. WebSocket connection provides live progress updates to frontend
5. Results are aggregated and stored in PostgreSQL with file references in MinIO

### Error Handling & Resilience

- Comprehensive file format validation on both frontend and backend
- Retry logic with exponential backoff for AI API calls (using Tenacity)
- React Error Boundary for UI crashes
- Connection status monitoring and graceful degradation
- Distributed task recovery through Celery's built-in mechanisms

### Development Workflow

The codebase supports hot-reload development with Docker volume mounting for backend services and Vite HMR for frontend. The frontend proxies API requests to the backend during development, enabling seamless full-stack development experience.

## Testing & Code Quality

### Current Status

The project currently focuses on functionality and deployment. No formal testing or linting frameworks are configured yet.

### TypeScript Type Checking

- Frontend uses strict TypeScript configuration with compiler-based linting
- `cd frontend && npx tsc --noEmit` - Type check without emitting files

### Docker Health Checks

All services include health checks for monitoring:
- PostgreSQL: `pg_isready` command
- Redis: `redis-cli ping` command  
- MinIO: HTTP health endpoint check
- Orchestrator: `/health` endpoint check
- Celery Workers: `celery inspect ping` command

### Recommendations for Future Development

When implementing testing, consider:
- **Backend**: pytest, pytest-asyncio, pytest-cov for Python testing
- **Frontend**: Vitest + Testing Library for React component testing
- **Linting**: flake8/ruff for Python, ESLint for TypeScript
- **Formatting**: black for Python, Prettier for TypeScript

## CLI and External Tools

- Use `/usr/bin/curl` for curl calls