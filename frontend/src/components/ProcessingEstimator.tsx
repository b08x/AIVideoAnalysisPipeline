// src/components/ProcessingEstimator.tsx
import React from 'react';
import { InfoIcon } from './Icons';

interface ProcessingEstimatorProps {
  videoFile: File | null;
}

const ProcessingEstimator: React.FC<ProcessingEstimatorProps> = ({ videoFile }) => {
  if (!videoFile) {
    return null;
  }

  // A very rough estimation: e.g., 1 minute of processing per 100MB of video file size.
  const sizeInMB = videoFile.size / (1024 * 1024);
  const estimatedMinutes = Math.max(1, Math.ceil(sizeInMB / 100)); // Ensure at least 1 minute

  return (
    <div className="mt-6 p-3 bg-brand-surface border border-brand-border rounded-lg flex items-center gap-3">
      <InfoIcon className="w-5 h-5 text-brand-accent flex-shrink-0" />
      <div>
        <p className="text-sm font-medium text-brand-text-primary">
          Estimated Processing Time: ~{estimatedMinutes} minute{estimatedMinutes > 1 ? 's' : ''}
        </p>
        <p className="text-xs text-brand-text-secondary">
          This is a rough estimate. Actual time may vary based on server load and content complexity.
        </p>
      </div>
    </div>
  );
};

export default ProcessingEstimator;
