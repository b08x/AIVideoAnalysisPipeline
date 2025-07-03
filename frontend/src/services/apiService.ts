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
    private baseUrl: string;
    private ws: WebSocket | null = null;

    constructor() {
        // Connect directly to backend - no proxy
        this.baseUrl = import.meta.env.VITE_APP_API_URL || 'http://localhost:8000';
    }

    public async uploadAndProcess(
        videoFile: File,
        subtitleFile: File,
        modelConfig: ModelConfig,
        onProgress: (progress: number) => void
    ): Promise<UploadResponse> {
        const formData = new FormData();
        formData.append('video', videoFile);
        formData.append('subtitle', subtitleFile);
        formData.append('config', JSON.stringify(modelConfig));

        // Connect directly to backend
        const url = `${this.baseUrl}/api/v1/jobs`;
        return uploadWithProgress<UploadResponse>(url, formData, onProgress);
    }

    public async getJobStatus(jobId: string): Promise<JobResponse> {
        const fn = async () => {
            const response = await fetch(`${this.baseUrl}/api/v1/jobs/${jobId}`);
            if (!response.ok) {
                throw new ApiError('Failed to get job status', response.status);
            }
            return response.json();
        };
        return withRetry(fn, 5, 2000);
    }

    public async cancelJob(jobId: string): Promise<void> {
        const response = await fetch(`${this.baseUrl}/api/v1/jobs/${jobId}`, {
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
        // Build WebSocket URL for direct backend connection
        const wsProtocol = this.baseUrl.startsWith('https') ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//localhost:8000/api/v1/jobs/${jobId}/progress`;
        
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
