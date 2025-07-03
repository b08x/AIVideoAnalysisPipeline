// src/utils/fileValidation.ts

/**
 * Validates a video file based on its size and MIME type.
 * @param file The video file to validate.
 * @returns A string containing an error message if validation fails, otherwise null.
 */
export const validateVideoFile = (file: File): string | null => {
  const maxSize = 2 * 1024 * 1024 * 1024; // 2GB
  const allowedTypes = ['video/mp4', 'video/webm', 'video/ogg', 'video/x-matroska', 'video/avi'];

  if (file.size > maxSize) {
    return 'Video file is too large. Please select a file smaller than 2GB.';
  }

  if (!allowedTypes.includes(file.type)) {
    // Also check extension for files like .mkv that might not have a perfect MIME type
    const fileExtension = `.${file.name.split('.').pop()}`;
    const allowedExtensions = ['.mp4', '.webm', '.ogg', '.mkv', '.avi'];
    if (!allowedExtensions.includes(fileExtension)) {
        return 'Unsupported video format. Please use MP4, WebM, OGG, MKV, or AVI.';
    }
  }

  return null;
};

/**
 * Validates a subtitle file based on its size and file extension.
 * @param file The subtitle file to validate.
 * @returns A string containing an error message if validation fails, otherwise null.
 */
export const validateSubtitleFile = (file: File): string | null => {
  const maxSize = 10 * 1024 * 1024; // 10MB
  const allowedExtensions = ['.vtt', '.srt', '.ass'];

  if (file.size > maxSize) {
    return 'Subtitle file is too large. Please select a file smaller than 10MB.';
  }

  const fileExtension = `.${file.name.split('.').pop()?.toLowerCase()}`;
  if (!allowedExtensions.includes(fileExtension)) {
    return 'Unsupported subtitle format. Please use VTT, SRT, or ASS.';
  }

  return null;
};
