# AI Video Analysis Pipeline

A comprehensive, full-stack application that performs deep video content analysis using advanced AI models. The system intelligently processes videos with subtitle files through a distributed backend pipeline and presents results via a modern React frontend.

## 🎯 Overview

The AI Video Analysis Pipeline transforms raw video content into structured insights by:

- **Parsing & Analyzing Subtitles**: Extracts meaning from VTT/SRT/ASS subtitle files with AI-powered summarization
- **Topic Modeling**: Identifies and clusters content themes using sentence-transformers and K-Means clustering
- **Frame Extraction**: Intelligently extracts keyframes based on scene changes and topic boundaries
- **Visual Analysis**: Analyzes video frames with computer vision (OCR, UI detection, scene understanding)
- **Comprehensive Reporting**: Generates detailed Markdown and PDF reports with all insights

## 🏗️ Architecture

### System Design

The application uses a **distributed microservices architecture** with the following components:

```shell
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI       │    │   Celery        │
│   (Vite + TS)   │◄──►│   Orchestrator  │◄──►│   Workers (4)   │
│   Port 3000     │    │   Port 8000     │    │   Distributed   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       ▼
         │              ┌─────────────────┐    ┌─────────────────┐
         │              │   PostgreSQL    │    │     Redis       │
         │              │   (Metadata)    │    │  (Task Queue)   │
         │              │   Port 5432     │    │   Port 6379     │
         │              └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 ▼
                       ┌─────────────────┐
                       │     MinIO       │
                       │ (Object Storage)│
                       │   Port 9000     │
                       └─────────────────┘
```

### Backend Services

**Core Services:**

- **Orchestrator** (`FastAPI`, Port 8000): Main API gateway, job management, WebSocket connections
- **4 Celery Workers**: Distributed processing for specialized tasks
- **PostgreSQL**: Job metadata, results, and state management
- **Redis**: Message broker for Celery task queue
- **MinIO**: S3-compatible object storage for files and generated reports

**Worker Services:**

- **Subtitle Processor**: Parses subtitle files, generates summaries, performs topic modeling
- **Video Processor**: Validates video files, extracts frames, segments content
- **Vision Analyzer**: Analyzes frames with AI vision models, performs OCR and UI detection
- **Documentation Service**: Generates comprehensive Markdown and PDF reports

### Frontend Architecture

- **React 19** with **TypeScript** for type safety
- **Vite** for fast development and optimized builds
- **WebSocket** integration for real-time progress updates
- **Comprehensive error handling** with graceful degradation
- **Feature flag system** for controlled feature rollouts

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** (for backend services)
- **Node.js 18+** (for frontend development)
- **API Keys**: OpenRouter API key, Gemini API key

### 1. Backend Setup

```bash
# Clone the repository
git clone <repository-url>
cd AIVideoAnalysisPipeline

# Configure environment variables
cp backend/.env.template backend/.env
# Edit backend/.env with your API keys:
# OPENROUTER_API_KEY=your_openrouter_key
# GEMINI_API_KEY=your_gemini_key

# Start all backend services
docker-compose -f docker-compose.dev.yml up --build
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Configure frontend environment
cp .env.local.example .env.local
# Edit .env.local if needed

# Start development server
npm run dev
```

### 3. Access the Application

- **Frontend**: <http://localhost:3000>
- **Backend API**: <http://localhost:8000>
- **MinIO Console**: <http://localhost:9001> (admin/admin123)

## 📊 Processing Pipeline

The system implements a **7-stage asynchronous pipeline**:

### Stage 1: Subtitle Processing

- **Input**: VTT/SRT/ASS subtitle files
- **Processing**: Parse timestamps, extract text, generate AI summaries
- **Output**: Structured utterances with metadata

### Stage 2: Topic Modeling

- **Input**: Processed utterances
- **Processing**: Generate embeddings with sentence-transformers, cluster with K-Means
- **Output**: Topic clusters with named themes

### Stage 3: Video Validation & Segmentation

- **Input**: Video files and topic boundaries
- **Processing**: Validate video format, segment based on topics
- **Output**: Video segments aligned with content themes

### Stage 4: Frame Extraction

- **Input**: Video segments
- **Processing**: Extract keyframes using histogram-based scene change detection
- **Output**: Representative frames for each segment

### Stage 5: Visual Analysis

- **Input**: Extracted frames
- **Processing**:
  - **Computer Vision**: Object detection, scene understanding
  - **OCR**: Text extraction with EasyOCR
  - **UI Detection**: Interface element recognition
  - **AI Vision**: Scene description with Gemini Vision API
- **Output**: Comprehensive frame analysis with detected elements

### Stage 6: Report Generation

- **Input**: All processed data (utterances, topics, visual analyses)
- **Processing**: Generate structured reports using Jinja2 templates
- **Output**: Markdown and PDF reports with complete insights

### Stage 7: Completion

- **WebSocket notifications** for real-time updates
- **File storage** in MinIO for persistent access
- **Metadata storage** in PostgreSQL for search and retrieval

## 🔧 Development

### Backend Development

```bash
# Start services in development mode
docker-compose -f docker-compose.dev.yml up --build

# View logs for specific service
docker-compose -f docker-compose.dev.yml logs -f orchestrator

# Access orchestrator shell for debugging
docker-compose -f docker-compose.dev.yml exec orchestrator bash

# Stop all services
docker-compose -f docker-compose.dev.yml down
```

### Frontend Development

```bash
cd frontend

# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Analyze bundle size
npm run analyze
```

### Environment Configuration

**Backend** (`backend/.env`):

```env
# Required API Keys
OPENROUTER_API_KEY=your_openrouter_key
GEMINI_API_KEY=your_gemini_key

# Database Configuration
POSTGRES_DB=video_processing
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev_password

# Redis Configuration
REDIS_URL=redis://redis:6379

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
```

**Frontend** (`frontend/.env.local`):

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# Feature Flags
VITE_ENABLE_ADVANCED_FEATURES=true
```

## 🔍 AI Models & Integration

### Supported Models

**Text Analysis**:

- **OpenAI GPT Models** (via OpenRouter): Text summarization, topic naming
- **Sentence Transformers**: Semantic embeddings for topic clustering

**Vision Analysis**:

- **Google Gemini Pro Vision**: Frame description and scene understanding
- **Google Gemini 2.5 Flash**: Fast visual analysis
- **Google Gemini 2.0 Flash**: Latest generation visual AI

**Computer Vision**:

- **EasyOCR**: Text extraction from video frames
- **OpenCV**: Frame extraction and image processing

### Configuration Options

The system supports extensive AI model configuration:

- **Temperature**: Controls randomness in AI responses (0.0-1.0)
- **Top-P**: Controls diversity in token selection (0.0-1.0)
- **Top-K**: Limits the token selection pool (1-100)
- **Model Selection**: Choose between different Gemini variants

## 🛠️ Key Features

### Real-time Processing

- **WebSocket connections** for live progress updates
- **Distributed processing** with automatic load balancing
- **Progress tracking** with estimated completion times

### Comprehensive Analysis

- **Multi-format subtitle support** (VTT, SRT, ASS)
- **Advanced topic modeling** with semantic clustering
- **Computer vision integration** for frame analysis
- **OCR capabilities** for text extraction from video

### Robust Error Handling

- **Retry logic** with exponential backoff for API calls
- **Connection status monitoring** with graceful degradation
- **React Error Boundaries** for UI crash recovery
- **Comprehensive logging** for debugging and monitoring

### Modern Development Experience

- **Hot reload** for both frontend and backend
- **TypeScript** for type safety across the entire stack
- **Docker containers** for consistent development environments
- **Feature flags** for controlled feature rollouts

## 📁 Project Structure

```
AIVideoAnalysisPipeline/
├── backend/
│   ├── base/                     # Base Docker image with common dependencies
│   ├── orchestrator/             # FastAPI main service
│   │   ├── api/                  # API endpoints (jobs, websocket)
│   │   ├── models.py             # Database models
│   │   └── main.py               # FastAPI application
│   ├── subtitle_processor/       # Subtitle parsing and analysis
│   │   ├── parsers.py            # VTT/SRT/ASS parsers
│   │   ├── summarizer.py         # AI summarization
│   │   └── topic_extractor.py    # Topic modeling
│   ├── video_processor/          # Video processing and frame extraction
│   │   ├── frame_extractor.py    # OpenCV frame extraction
│   │   ├── segmenter.py          # Video segmentation
│   │   └── validator.py          # Video format validation
│   ├── vision_analyzer/          # Visual analysis with AI
│   │   ├── analyzer.py           # Gemini Vision integration
│   │   ├── ui_detector.py        # UI element detection
│   │   └── prompts.py            # AI prompts for analysis
│   └── documentation/            # Report generation
│       ├── generator.py          # Report creation
│       ├── exporters.py          # PDF/Markdown export
│       └── templates/            # Jinja2 templates
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API communication
│   │   ├── types/                # TypeScript definitions
│   │   ├── utils/                # Utility functions
│   │   └── contexts/             # React contexts
│   ├── package.json              # Frontend dependencies
│   └── vite.config.ts            # Vite configuration
├── docker-compose.dev.yml        # Development environment
└── README.md                     # This file
```

## 🚦 API Documentation

### Job Management Endpoints

**POST** `/api/v1/jobs`

- Create new analysis job
- Upload video and subtitle files
- Configure AI model parameters

**GET** `/api/v1/jobs/{job_id}`

- Get job status and results
- Download generated reports

**DELETE** `/api/v1/jobs/{job_id}`

- Cancel running job
- Clean up resources

### WebSocket Events

**Connection**: `/api/v1/ws/{job_id}`

- Real-time progress updates
- Stage transition notifications
- Error and completion events

## 🔒 Security & Best Practices

### Security Features

- **API key management** with environment variables
- **CORS configuration** for secure cross-origin requests
- **Input validation** for all file uploads
- **SQL injection prevention** with SQLAlchemy ORM
- **Container isolation** with Docker

### Best Practices

- **Never commit API keys** to version control
- **Use environment variables** for all sensitive configuration
- **Implement proper error handling** throughout the application
- **Follow TypeScript strict mode** for type safety
- **Use Docker** for consistent environments

## 📈 Performance & Scalability

### Optimization Features

- **Async processing** with Celery for CPU-intensive tasks
- **Distributed workers** for parallel processing
- **Object storage** with MinIO for efficient file handling
- **Database indexing** for fast job lookups
- **Frontend code splitting** for faster load times

### Monitoring & Debugging

- **Comprehensive logging** across all services
- **Health checks** for all Docker containers
- **Real-time progress tracking** with WebSocket connections
- **Bundle analysis** for frontend performance optimization

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes** following the existing code style
4. **Add tests** for new functionality
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to the branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **OpenAI** for providing advanced language models
- **Google** for Gemini Vision API
- **The open-source community** for the amazing tools and libraries that make this project possible

---

**Built with ❤️ using React, FastAPI, Docker, and AI**
