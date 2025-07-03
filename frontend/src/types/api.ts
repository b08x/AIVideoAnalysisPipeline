// frontend/src/types/api.ts

// Represents the configuration for the analysis job
export interface ModelConfig {
    summarization_model: string;
    vision_model: string;
    topic_model: string;
}

// Represents a single utterance from the subtitle analysis
export interface Utterance {
    start_time: number;
    end_time: number;
    text: string;
    summary?: string;
}

// Represents a detected topic from the subtitle analysis
export interface Topic {
    topic_id: number;
    topic_name: string;
    utterance_indices: number[];
    summary?: string;
}

// Represents a detected element within a video frame
export interface DetectedElement {
    type: "text" | "button" | "input" | "image" | "icon" | "code_block" | "diagram";
    content: string;
    bounding_box: [number, number, number, number];
    confidence: number;
}

// Represents the full analysis of a single video frame
export interface FrameAnalysis {
    frame_id: string;
    screen_type: "code_editor" | "terminal" | "diagram" | "webpage" | "presentation" | "other";
    description: string;
    detected_elements: DetectedElement[];
    context_relevance_score: number;
}

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
    stage: string; // e.g., 'parsing_subtitles', 'visual_analysis'
    status: 'in_progress' | 'completed' | 'failed';
    progress_percent: number;
    details?: string;
    eta_seconds?: number;
    stage_data?: { // Optional data payload for a specific stage
        utterances?: Utterance[];
        topics?: Topic[];
    };
}
