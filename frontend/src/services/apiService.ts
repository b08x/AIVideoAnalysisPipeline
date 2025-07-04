// src/services/apiService.ts (Finalized as Primary Service)
import {
    UploadResponse,
    JobResponse,
    ProgressUpdate,
    ModelConfig,
    FrameAnalysis
} from '../types';
import { ApiError, withRetry } from '../utils/errorHandling';
import { uploadWithProgress } from '../utils/uploadWithProgress';

class ApiService {
    private ws: WebSocket | null = null;

    constructor() {
        // Base URL is no longer needed, as we'll use relative paths
    }

    public async uploadAndProcess(
        videoFile: File,
        subtitleFile: File,
        modelConfig: ModelConfig,
        onProgress: (progress: number) => void
    ): Promise<UploadResponse> {
        const formData = new FormData();
        formData.append('video_file', videoFile);
        formData.append('subtitle_file', subtitleFile);
        formData.append('config', JSON.stringify(modelConfig));

        // Use a relative URL for the API endpoint
        const url = '/api/v1/jobs';
        return uploadWithProgress<UploadResponse>(url, formData, onProgress);
    }

    public async getJobStatus(jobId: string): Promise<JobResponse> {
        const fn = async () => {
            // Use a relative URL
            const response = await fetch(`/api/v1/jobs/${jobId}`);
            if (!response.ok) {
                throw new ApiError('Failed to get job status', response.status);
            }
            return response.json();
        };
        return withRetry(fn, 5, 2000);
    }

    public async cancelJob(jobId: string): Promise<void> {
        // Use a relative URL
        const response = await fetch(`/api/v1/jobs/${jobId}`, {
            method: 'DELETE',
        });
        if (!response.ok && response.status !== 204) {
            throw new ApiError('Failed to cancel job', response.status);
        }
    }

    public connectToProgress(
        jobId: string,
        onProgress: (data: ProgressUpdate) => void,
        onError: (error: string) => void
    ): void {
        if (this.ws) {
            this.ws.close();
        }
        // Dynamically construct WebSocket URL for reverse proxy
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsHost = window.location.host;
        const wsUrl = `${wsProtocol}//${wsHost}/ws/jobs/${jobId}/progress`;
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data) as ProgressUpdate;
                onProgress(data);
            } catch (error) {
                onError('Failed to parse progress data.');
            }
        };
        this.ws.onerror = () => { onError('WebSocket connection failed.'); };
        this.ws.onclose = () => { console.log('WebSocket connection closed.'); };
    }

    public disconnectProgress(): void {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
    }
}

export const apiService = new ApiService();
