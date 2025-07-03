// frontend/src/utils/errorHandling.ts

/**
 * Custom error class for API-specific errors.
 */
export class ApiError extends Error {
    constructor(
        message: string,
        public status?: number,
        public details?: any
    ) {
        super(message);
        this.name = 'ApiError';
    }
}

/**
 * Translates an error object into a user-friendly string.
 * @param error The error object (can be of any type).
 * @returns A user-friendly error message.
 */
export const handleApiError = (error: unknown): string => {
    if (error instanceof ApiError) {
        if (error.status === 413) {
            return 'File too large. Please ensure the video is under 2GB and subtitles are under 10MB.';
        }
        if (error.status === 429) {
            return 'Too many requests. Please wait a moment before trying again.';
        }
        if (error.status && error.status >= 500) {
            return 'A server error occurred. The team has been notified. Please try again later.';
        }
        return error.message;
    }
    if (error instanceof Error) {
        return error.message;
    }
    return 'An unexpected error occurred. Please check your connection and try again.';
};

/**
 * A higher-order function to retry an async operation with exponential backoff.
 * @param fn The async function to retry.
 * @param maxRetries The maximum number of retries.
 * @param delay The initial delay in milliseconds.
 * @returns The result of the async function.
 */
export const withRetry = async <T>(
    fn: () => Promise<T>,
    maxRetries: number = 3,
    delay: number = 1000
): Promise<T> => {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await fn();
        } catch (error) {
            if (i === maxRetries - 1) throw error;
            const backoffDelay = delay * Math.pow(2, i);
            console.warn(`Request failed. Retrying in ${backoffDelay}ms... (Attempt ${i + 1}/${maxRetries})`);
            await new Promise(resolve => setTimeout(resolve, backoffDelay));
        }
    }
    throw new Error('Max retries exceeded');
};
