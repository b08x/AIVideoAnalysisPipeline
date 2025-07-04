// src/components/DetailedProgressTracker.tsx
import React, { useState, useEffect } from 'react';
import { CheckCircleIcon, LoaderIcon, AlertTriangleIcon, ClockIcon, ActivityIcon } from './Icons';

export interface StageProgress {
  stage: string;
  progress: number;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  description?: string;
  startTime?: string;
  endTime?: string;
  steps?: StepProgress[];
  details?: Record<string, any>;
}

export interface StepProgress {
  step: string;
  progress: number;
  current: number;
  total: number;
  description?: string;
  details?: Record<string, any>;
}

export interface DetailedProgress {
  stages: Record<string, StageProgress>;
  currentStage?: string;
  overallProgress: number;
  startTime?: string;
  estimatedTimeRemaining?: number;
}

interface DetailedProgressTrackerProps {
  progress: DetailedProgress;
  className?: string;
}

const STAGE_CONFIG = {
  'initialization': { 
    name: 'Initialization', 
    description: 'Setting up the analysis pipeline',
    icon: '🚀',
    color: 'bg-blue-500'
  },
  'subtitle_processing': { 
    name: 'Subtitle Processing', 
    description: 'Parsing and analyzing subtitle content',
    icon: '📝',
    color: 'bg-green-500'
  },
  'video_validation': { 
    name: 'Video Validation', 
    description: 'Validating video format and properties',
    icon: '🎬',
    color: 'bg-purple-500'
  },
  'frame_extraction': { 
    name: 'Frame Extraction', 
    description: 'Extracting keyframes for analysis',
    icon: '🖼️',
    color: 'bg-orange-500'
  },
  'visual_analysis': { 
    name: 'Visual Analysis', 
    description: 'Analyzing frames with AI vision models',
    icon: '👁️',
    color: 'bg-cyan-500'
  },
  'report_generation': { 
    name: 'Report Generation', 
    description: 'Creating comprehensive analysis report',
    icon: '📊',
    color: 'bg-indigo-500'
  },
};

const formatDuration = (seconds: number): string => {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m ${Math.round(seconds % 60)}s`;
  return `${Math.round(seconds / 3600)}h ${Math.round((seconds % 3600) / 60)}m`;
};

const formatTimeRemaining = (seconds?: number): string => {
  if (!seconds) return 'Calculating...';
  return `~${formatDuration(seconds)} remaining`;
};

const StageCard: React.FC<{ 
  stageKey: string; 
  stage: StageProgress; 
  isActive: boolean;
  isExpanded: boolean;
  onToggleExpand: () => void;
}> = ({ stageKey, stage, isActive, isExpanded, onToggleExpand }) => {
  const config = STAGE_CONFIG[stageKey as keyof typeof STAGE_CONFIG];
  if (!config) return null;

  const getStatusIcon = () => {
    switch (stage.status) {
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-400" />;
      case 'failed':
        return <AlertTriangleIcon className="w-5 h-5 text-red-400" />;
      case 'in_progress':
        return <LoaderIcon className="w-5 h-5 text-blue-400 animate-spin" />;
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-gray-400" />;
    }
  };

  const getProgressColor = () => {
    switch (stage.status) {
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      case 'in_progress': return 'bg-blue-500';
      default: return 'bg-gray-400';
    }
  };

  return (
    <div className={`border rounded-lg transition-all duration-300 ${
      isActive ? 'border-blue-400 bg-blue-50/5' : 'border-gray-600 bg-gray-800/50'
    }`}>
      <div 
        className="p-4 cursor-pointer hover:bg-gray-700/30 transition-colors"
        onClick={onToggleExpand}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="text-2xl">{config.icon}</div>
            <div>
              <h3 className="font-semibold text-white">{config.name}</h3>
              <p className="text-sm text-gray-400">{stage.description || config.description}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {getStatusIcon()}
            <div className="text-right">
              <div className="text-sm font-mono text-white">{stage.progress}%</div>
              {stage.status === 'in_progress' && (
                <div className="text-xs text-gray-400">Active</div>
              )}
            </div>
          </div>
        </div>
        
        {/* Progress bar */}
        <div className="mt-3 w-full bg-gray-700 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-500 ${getProgressColor()}`}
            style={{ width: `${stage.progress}%` }}
          />
        </div>
      </div>

      {/* Expanded details */}
      {isExpanded && (
        <div className="px-4 pb-4 border-t border-gray-600">
          <div className="mt-3 space-y-2">
            {stage.steps && stage.steps.map((step, index) => (
              <div key={step.step} className="flex justify-between items-center text-sm">
                <span className="text-gray-300">
                  {step.description || step.step}
                </span>
                <span className="font-mono text-gray-400">
                  {step.current}/{step.total} ({step.progress}%)
                </span>
              </div>
            ))}
            
            {stage.details && Object.keys(stage.details).length > 0 && (
              <div className="mt-3 p-2 bg-gray-800 rounded text-xs">
                <div className="text-gray-400 mb-1">Details:</div>
                {Object.entries(stage.details).map(([key, value]) => (
                  <div key={key} className="text-gray-300">
                    <span className="text-gray-500">{key}:</span> {JSON.stringify(value)}
                  </div>
                ))}
              </div>
            )}
            
            {stage.startTime && (
              <div className="text-xs text-gray-400 mt-2">
                Started: {new Date(stage.startTime).toLocaleTimeString()}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const DetailedProgressTracker: React.FC<DetailedProgressTrackerProps> = ({ 
  progress, 
  className = '' 
}) => {
  const [expandedStages, setExpandedStages] = useState<Set<string>>(new Set());
  
  // Auto-expand the current stage
  useEffect(() => {
    if (progress.currentStage) {
      setExpandedStages(prev => new Set([...prev, progress.currentStage!]));
    }
  }, [progress.currentStage]);

  const toggleStageExpansion = (stageKey: string) => {
    setExpandedStages(prev => {
      const newSet = new Set(prev);
      if (newSet.has(stageKey)) {
        newSet.delete(stageKey);
      } else {
        newSet.add(stageKey);
      }
      return newSet;
    });
  };

  const stageOrder = [
    'initialization',
    'subtitle_processing', 
    'video_validation',
    'frame_extraction',
    'visual_analysis',
    'report_generation'
  ];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Overall Progress Header */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-600">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ActivityIcon className="w-5 h-5" />
            Processing Progress
          </h2>
          <div className="text-right">
            <div className="text-2xl font-bold text-white">{progress.overallProgress}%</div>
            {progress.estimatedTimeRemaining && (
              <div className="text-sm text-gray-400 flex items-center gap-1">
                <ClockIcon className="w-4 h-4" />
                {formatTimeRemaining(progress.estimatedTimeRemaining)}
              </div>
            )}
          </div>
        </div>
        
        {/* Overall progress bar */}
        <div className="w-full bg-gray-700 rounded-full h-3">
          <div
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-3 rounded-full transition-all duration-500"
            style={{ width: `${progress.overallProgress}%` }}
          />
        </div>
        
        {progress.startTime && (
          <div className="text-xs text-gray-400 mt-2">
            Started: {new Date(progress.startTime).toLocaleString()}
          </div>
        )}
      </div>

      {/* Stage Progress Cards */}
      <div className="space-y-3">
        {stageOrder.map(stageKey => {
          const stage = progress.stages[stageKey];
          if (!stage) return null;
          
          return (
            <StageCard
              key={stageKey}
              stageKey={stageKey}
              stage={stage}
              isActive={progress.currentStage === stageKey}
              isExpanded={expandedStages.has(stageKey)}
              onToggleExpand={() => toggleStageExpansion(stageKey)}
            />
          );
        })}
      </div>
    </div>
  );
};

export default DetailedProgressTracker;