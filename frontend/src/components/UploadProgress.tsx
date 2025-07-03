// src/components/UploadProgress.tsx
import React from 'react';
import { UploadCloudIcon } from './Icons';

interface UploadProgressProps {
  progress: number;
}

const UploadProgress: React.FC<UploadProgressProps> = ({ progress }) => {
  // Don't render if upload hasn't started or is complete
  if (progress <= 0 || progress >= 100) return null;

  return (
    <div className="w-full bg-brand-surface p-4 rounded-lg border border-brand-border mb-6">
      <div className="flex items-center gap-3 mb-2">
        <UploadCloudIcon className="w-5 h-5 text-brand-accent" />
        <p className="text-sm font-medium text-brand-text-primary">Uploading files to the processing engine...</p>
      </div>
      <div className="w-full bg-brand-border rounded-full h-2.5">
        <div
          className="bg-brand-accent h-2.5 rounded-full transition-width duration-300 ease-linear"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      <p className="text-right text-xs font-mono text-brand-text-secondary mt-1">{Math.round(progress)}%</p>
    </div>
  );
};

export default UploadProgress;
