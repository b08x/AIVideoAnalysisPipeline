// src/types.ts (Finalized for Backend-Only Architecture)

// Represents the processing stage, used for the UI stepper.
export enum ProcessStage {
  Idle = "Idle",
  ParsingSubtitles = "Parsing Subtitles",
  Summarizing = "Summarizing Utterances",
  TopicModeling = "Modeling Topics",
  Segmenting = "Segmenting by Topic",
  FrameExtraction = "Extracting Frames",
  VisualAnalysis = "Analyzing Visuals",
  GeneratingReport = "Generating Report",
  Done = "Done"
}

// Represents a single utterance from the subtitle analysis (from backend)
export interface Utterance {
  start_time: number;
  end_time: number;
  text: string;
  summary?: string;
}

// Represents a detected topic from the subtitle analysis (from backend)
export interface Topic {
  topic_id: number;
  topic_name: string;
  utterance_indices: number[];
  summary?: string;
}

// Represents a detected element within a video frame (from backend)
export interface DetectedElement {
    type: "text" | "button" | "input" | "image" | "icon" | "code_block" | "diagram";
    content: string;
    bounding_box: [number, number, number, number];
    confidence: number;
}

// Represents the full analysis of a single video frame (from backend)
export interface FrameAnalysis {
    frame_id: string;
    screen_type: "code_editor" | "terminal" | "diagram" | "webpage" | "presentation" | "other";
    description: string;
    detected_elements: DetectedElement[];
    context_relevance_score: number;
}

// Simplified ModelConfig for backend
export type ModelName = 'gemini-2.5-pro' | 'gemini-2.5-flash' | 'gemini-2.5-flash-lite-preview-06-17' | 'gemini-2.0-flash';

export interface ModelConfig {
  model: ModelName;
  temperature: number;
  topP: number;
  topK: number;
}

// --- API Communication Types ---

// The response received after successfully creating a job
export interface UploadResponse {
    job_id: string;
    status: 'pending' | 'accepted';
    message: string;
}

// The detailed status and results of a job
export interface JobResponse {
    id: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    created_at: string;
    updated_at: string;
    results?: {
        utterances: Utterance[];
        topics: Topic[];
        visual_analyses: FrameAnalysis[];
        final_report_path: string;
    };
    error?: string;
}

// The structure of real-time progress updates via WebSocket
export interface ProgressUpdate {
    job_id: string;
    stage: string;
    status: 'in_progress' | 'completed' | 'failed';
    progress_percent: number;
    details?: string;
    eta_seconds?: number;
    stage_data?: {
        utterances?: Utterance[];
        topics?: Topic[];
    };
}

// Represents the frontend's view of the job's progress
export interface JobProgress {
    jobId: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    currentStage: string;
    progress: number;
    eta?: number;
    error?: string;
}
