// frontend/src/utils/uploadWithProgress.ts
import { ApiError } from './errorHandling';

/**
 * Uploads a file using XMLHttpRequest to support progress tracking.
 * @param url The destination URL for the upload.
 * @param formData The FormData object containing the file and other data.
 * @param onProgress A callback function to report upload progress (0-100).
 * @returns A promise that resolves with the parsed JSON response.
 */
export const uploadWithProgress = <T>(
    url: string,
    formData: FormData,
    onProgress: (progress: number) => void
): Promise<T> => {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        // Listen for progress events
        xhr.upload.addEventListener('progress', (event) => {
            if (event.lengthComputable) {
                const progress = (event.loaded / event.total) * 100;
                onProgress(progress);
            }
        });

        // Handle completion
        xhr.addEventListener('load', () => {
            onProgress(100); // Ensure progress bar completes
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const jsonResponse = JSON.parse(xhr.response);
                    resolve(jsonResponse as T);
                } catch (e) {
                    reject(new ApiError('Failed to parse server response.', xhr.status, xhr.response));
                }
            } else {
                reject(new ApiError(xhr.statusText || 'Upload failed', xhr.status, xhr.response));
            }
        });

        // Handle errors
        xhr.addEventListener('error', () => {
            reject(new ApiError('An error occurred during the upload.', xhr.status));
        });

        xhr.addEventListener('abort', () => {
            reject(new ApiError('Upload was aborted.', xhr.status));
        });

        xhr.open('POST', url, true);
        // Add any necessary headers here, e.g., for authentication
        // xhr.setRequestHeader('Authorization', `Bearer ${token}`);
        xhr.send(formData);
    });
};
