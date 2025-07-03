// src/App.tsx (Final UI/UX)
import React, { useState, useCallback, useEffect, useRef } from 'react';
import { ProcessStage, Utterance, Topic, ModelConfig, ModelName, JobProgress, ProgressUpdate, JobResponse, FrameAnalysis } from './types';
import { apiService } from './services/apiService';
import { handleApiError } from './utils/errorHandling';
import { validateVideoFile, validateSubtitleFile } from './utils/fileValidation';
import { CheckCircleIcon, PlayIcon, LoaderIcon, FileTextIcon, EyeIcon, FilmIcon, BookOpenIcon, BotIcon, XIcon, UploadCloudIcon, SlidersHorizontalIcon, InfoIcon, AlertTriangleIcon, ServerIcon } from './components/Icons';
import ReportModal from './components/ReportModal';
import UploadProgress from './components/UploadProgress';
import EnhancedFileUploader from './components/upload/EnhancedFileUploader';
import ServerStatusIndicator from './components/ServerStatusIndicator';
import ProcessingEstimator from './components/ProcessingEstimator';

// --- UI COMPONENTS ---
const Tooltip: React.FC<{text: string, children: React.ReactNode}> = ({ text, children }) => (<div className="relative flex items-center group">{children}<div className="absolute left-0 -top-2 ml-8 w-48 px-2 py-1 bg-gray-900 text-white text-xs rounded-md shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none z-10 border border-brand-border">{text}</div></div>);
const AVAILABLE_MODELS: ModelName[] = ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.5-flash-lite-preview-06-17', 'gemini-2.0-flash'];
const ModelConfigurator: React.FC<{config: ModelConfig, setConfig: (c: ModelConfig) => void}> = ({ config, setConfig }) => { return ( <div className="w-full mt-6 pt-6 border-t border-brand-border"><h3 className="text-lg font-semibold text-brand-text-primary mb-4 flex items-center gap-2"><SlidersHorizontalIcon className="w-5 h-5"/>Model Configuration</h3><div className="space-y-4"><div><label htmlFor="model" className="block text-sm font-medium text-brand-text-secondary mb-2">Analysis Model</label><select id="model" name="model" value={config.model} onChange={(e) => setConfig({...config, model: e.target.value as ModelName})} className="w-full bg-brand-surface border border-brand-border rounded-md px-3 py-2 text-brand-text-primary focus:ring-brand-accent focus:border-brand-accent">{AVAILABLE_MODELS.map(modelName => (<option key={modelName} value={modelName}>{modelName}</option>))}</select></div><div><div className="flex justify-between items-center mb-1"><Tooltip text="Controls randomness."><label htmlFor="temperature" className="text-sm font-medium text-brand-text-secondary flex items-center gap-1.5 cursor-help">Temperature <InfoIcon className="w-3.5 h-3.5"/></label></Tooltip><span className="text-sm font-mono text-brand-text-primary">{config.temperature.toFixed(2)}</span></div><input type="range" name="temperature" min="0" max="1" step="0.05" value={config.temperature} onChange={(e) => setConfig({...config, temperature: parseFloat(e.target.value)})} className="w-full h-2 bg-brand-border rounded-lg appearance-none cursor-pointer accent-brand-accent"/></div><div><div className="flex justify-between items-center mb-1"><Tooltip text="Controls diversity."><label htmlFor="topP" className="text-sm font-medium text-brand-text-secondary flex items-center gap-1.5 cursor-help">Top P <InfoIcon className="w-3.5 h-3.5"/></label></Tooltip><span className="text-sm font-mono text-brand-text-primary">{config.topP.toFixed(2)}</span></div><input type="range" name="topP" min="0" max="1" step="0.05" value={config.topP} onChange={(e) => setConfig({...config, topP: parseFloat(e.target.value)})} className="w-full h-2 bg-brand-border rounded-lg appearance-none cursor-pointer accent-brand-accent"/></div><div><div className="flex justify-between items-center mb-1"><Tooltip text="Limits sampling pool."><label htmlFor="topK" className="text-sm font-medium text-brand-text-secondary flex items-center gap-1.5 cursor-help">Top K <InfoIcon className="w-3.5 h-3.5"/></label></Tooltip><span className="text-sm font-mono text-brand-text-primary">{config.topK}</span></div><input type="range" name="topK" min="1" max="100" step="1" value={config.topK} onChange={(e) => setConfig({...config, topK: parseInt(e.target.value)})} className="w-full h-2 bg-brand-border rounded-lg appearance-none cursor-pointer accent-brand-accent"/></div></div></div>);};

// --- MAIN APP COMPONENT ---
const App: React.FC = () => {
  const [appState, setAppState] = useState<'landing' | 'processing'>('landing');
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [subtitleFile, setSubtitleFile] = useState<File | null>(null);
  const [error, setError] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [modelConfig, setModelConfig] = useState<ModelConfig>({ model: 'gemini-2.5-flash', temperature: 0.7, topP: 0.95, topK: 40 });
  
  const [stage, setStage] = useState<ProcessStage>(ProcessStage.Idle);
  const [utterances, setUtterances] = useState<Utterance[]>([]);
  const [topics, setTopics] = useState<Topic[]>([]);
  const [visualAnalyses, setVisualAnalyses] = useState<FrameAnalysis[]>([]);
  const [finalReport, setFinalReport] = useState<string>('');
  const [showReport, setShowReport] = useState<boolean>(false);
  
  const [jobId, setJobId] = useState<string>('');
  const [jobProgress, setJobProgress] = useState<JobProgress | null>(null);
  const [canCancel, setCanCancel] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const pollingIntervalRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      apiService.disconnectProgress();
      if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
    };
  }, []);
  
  const resetState = useCallback(() => {
      setAppState('landing');
      setIsProcessing(false);
      setCanCancel(false);
      setJobId('');
      setJobProgress(null);
      setUploadProgress(0);
      setStage(ProcessStage.Idle);
      setUtterances([]);
      setTopics([]);
      setVisualAnalyses([]);
      setFinalReport('');
      if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
      apiService.disconnectProgress();
  }, []);

  const handleStartAnalysis = async () => {
    if (!videoFile || !subtitleFile) return;
    setError('');
    setIsProcessing(true);
    setAppState('processing');
    setCanCancel(true);
    setUploadProgress(0);
    setStage(ProcessStage.Idle);
    try {
        const response = await apiService.uploadAndProcess(videoFile, subtitleFile, modelConfig, setUploadProgress);
        setJobId(response.job_id);
        apiService.connectToProgress(response.job_id, handleProgressUpdate, handleProgressError);
        pollJobStatus(response.job_id);
    } catch (err) {
        setError(handleApiError(err));
        resetState();
    }
  };

  const handleProgressUpdate = (data: ProgressUpdate) => {
      const stageMapping: Record<string, ProcessStage> = {
          'parsing_subtitles': ProcessStage.ParsingSubtitles, 'summarizing_utterances': ProcessStage.Summarizing,
          'topic_modeling': ProcessStage.TopicModeling, 'video_segmentation': ProcessStage.Segmenting,
          'frame_extraction': ProcessStage.FrameExtraction, 'visual_analysis': ProcessStage.VisualAnalysis,
          'report_generation': ProcessStage.GeneratingReport,
      };
      setStage(stageMapping[data.stage] || stage);
      setJobProgress({ jobId: data.job_id, status: 'processing', currentStage: data.stage, progress: data.progress_percent, eta: data.eta_seconds });
      if (data.stage_data?.utterances) setUtterances(data.stage_data.utterances);
      if (data.stage_data?.topics) setTopics(data.stage_data.topics);
  };

  const handleProgressError = (errorMsg: string) => { setError(`Connection error: ${errorMsg}`); };

  const pollJobStatus = (currentJobId: string) => {
      if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
      pollingIntervalRef.current = window.setInterval(async () => {
          try {
              const status: JobResponse = await apiService.getJobStatus(currentJobId);
              if (status.status === 'completed') {
                  if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
                  apiService.disconnectProgress();
                  if (status.results) {
                      setUtterances(status.results.utterances);
                      setTopics(status.results.topics);
                      setVisualAnalyses(status.results.visual_analyses);
                      setFinalReport(status.results.final_report_path);
                  }
                  setStage(ProcessStage.Done);
                  setIsProcessing(false); setCanCancel(false); setShowReport(true);
              } else if (status.status === 'failed') {
                  if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
                  setError(status.error || 'Processing failed on the backend.');
                  resetState();
              }
          } catch (err) { console.error('Error polling job status:', err); }
      }, 5000);
  };

  const handleCancelJob = async () => {
      if (!jobId) return;
      try {
          await apiService.cancelJob(jobId);
          setError('Processing was cancelled by the user.');
      } catch (err) {
          setError(handleApiError(err));
      } finally {
          resetState();
      }
  };

  const STAGES = [ { id: ProcessStage.ParsingSubtitles, icon: <FileTextIcon className="w-5 h-5"/> }, { id: ProcessStage.Summarizing, icon: <BookOpenIcon className="w-5 h-5"/> }, { id: ProcessStage.TopicModeling, icon: <BotIcon className="w-5 h-5"/> }, { id: ProcessStage.Segmenting, icon: <FilmIcon className="w-5 h-5"/> }, { id: ProcessStage.FrameExtraction, icon: <FilmIcon className="w-5 h-5"/>}, { id: ProcessStage.VisualAnalysis, icon: <EyeIcon className="w-5 h-5"/> }, { id: ProcessStage.GeneratingReport, icon: <FileTextIcon className="w-5 h-5"/> } ];
  const currentStageIndex = STAGES.findIndex(s => s.id === stage);

  const renderLandingPage = () => (
    <div className="flex flex-col items-center justify-center min-h-[70vh]">
        <header className="text-center mb-10">
          <div className="flex justify-center mb-4">
            <ServerStatusIndicator />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight">AI Video Analysis Pipeline</h1>
          <p className="mt-4 text-lg text-brand-text-secondary max-w-3xl mx-auto">
            Upload your video and subtitle file, configure the model, and begin a deep-dive analysis powered by a robust backend pipeline.
          </p>
        </header>
        {error && (<div className="w-full max-w-3xl bg-red-900/50 border border-red-500 text-red-300 p-4 rounded-lg mb-6 text-center flex items-center gap-2"><AlertTriangleIcon className="w-5 h-5 flex-shrink-0"/><p>{error}</p></div>)}
        <div className="w-full max-w-3xl bg-brand-surface p-8 rounded-xl border border-brand-border shadow-2xl">
            <div className="flex flex-col md:flex-row gap-8">
                <EnhancedFileUploader file={videoFile} onFileSelect={setVideoFile} onFileClear={() => setVideoFile(null)} title="1. Upload Video" acceptedTypes="video/mp4,video/webm,video/ogg,video/x-matroska,.mkv,.avi" validationFn={validateVideoFile} icon="video"/>
                <EnhancedFileUploader file={subtitleFile} onFileSelect={setSubtitleFile} onFileClear={() => setSubtitleFile(null)} title="2. Upload Subtitles" acceptedTypes=".vtt,.srt,.ass" validationFn={validateSubtitleFile} icon="subtitle"/>
            </div>
            <ProcessingEstimator videoFile={videoFile} />
            <ModelConfigurator config={modelConfig} setConfig={setModelConfig} />
            <button onClick={handleStartAnalysis} disabled={!videoFile || !subtitleFile || isProcessing} className="w-full mt-8 bg-brand-accent text-white font-bold py-3 px-8 rounded-lg text-xl shadow-lg shadow-brand-accent-glow hover:bg-blue-500 transition-all duration-300 ease-in-out transform hover:scale-105 disabled:bg-brand-surface disabled:text-brand-text-secondary disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none flex items-center justify-center gap-3">{isProcessing ? <LoaderIcon className="animate-spin" /> : <PlayIcon />} {isProcessing ? 'Processing...' : 'Start Analysis'}</button>
        </div>
    </div>
  );
  
  const renderProcessingPage = () => (
    <div className="space-y-8">
        <div className="flex justify-between items-center"><h2 className="text-3xl font-bold">Processing Analysis</h2>{canCancel && <button onClick={handleCancelJob} className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors flex items-center gap-2"><XIcon className="w-5 h-5"/>Cancel</button>}</div>
        <UploadProgress progress={uploadProgress} />
        <div className="w-full px-4 sm:px-0"><div className="flex items-center">{STAGES.map((s, index) => (<React.Fragment key={s.id}><div className="flex flex-col items-center text-center"><div className={`w-10 h-10 rounded-full flex items-center justify-center transition-all duration-500 ${currentStageIndex >= index ? 'bg-brand-accent' : 'bg-brand-surface border-2 border-brand-border'}`}>{currentStageIndex > index ? <CheckCircleIcon className="w-6 h-6 text-white"/> : (isProcessing) ? <LoaderIcon className="w-6 h-6 text-white animate-spin"/> : s.icon}</div><p className={`mt-2 text-xs transition-colors duration-500 w-24 ${currentStageIndex >= index ? 'text-brand-text-primary' : 'text-brand-text-secondary'}`}>{s.id}</p></div>{index < STAGES.length - 1 && <div className={`flex-auto border-t-2 transition-colors duration-500 ${currentStageIndex > index ? 'border-brand-accent' : 'border-brand-border'}`}></div>}</React.Fragment>))}</div></div>
        <div className="bg-brand-surface border border-brand-border rounded-lg p-6 min-h-[400px]"><div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="lg:col-span-1"><h2 className="text-2xl font-bold mb-4">Transcript & Summaries</h2><div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">{utterances.map((u, idx) => (<div key={idx} className="bg-[#0D1117] p-3 rounded-md"><p className="text-brand-text-secondary text-sm"><span className="font-mono bg-gray-700 px-1.5 py-0.5 rounded">{u.start_time.toFixed(2)}s</span> {u.text}</p>{u.summary && (<p className="mt-2 text-sm text-cyan-300 border-l-2 border-cyan-500 pl-3 italic">{u.summary}</p>)}</div>))}</div></div>
            <div className="lg:col-span-1"><h2 className="text-2xl font-bold mb-4">Topics & Visual Analysis</h2><div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">{topics.map(topic => (<div key={topic.topic_id} className="bg-[#0D1117] p-4 rounded-lg border border-brand-border"><h3 className="font-bold text-lg text-emerald-400">{topic.topic_name}</h3><p className="text-sm text-brand-text-secondary mt-1 italic">{topic.summary || 'No summary available.'}</p></div>))}</div></div>
        </div></div>
        {stage === ProcessStage.Done && (<div className="text-center mt-8"><button onClick={() => setShowReport(true)} className="bg-emerald-600 text-white font-bold py-3 px-8 rounded-lg text-xl shadow-lg shadow-emerald-500/50 hover:bg-emerald-500 transition-all duration-300 ease-in-out transform hover:scale-105 flex items-center gap-3 mx-auto"><EyeIcon />View Full Report</button></div>)}
    </div>
  );

  return (
    <div className="min-h-screen bg-brand-bg text-brand-text-primary font-sans p-4 sm:p-6 lg:p-8">
      {showReport && <ReportModal report={finalReport} onClose={() => setShowReport(false)} />}
      <div className="max-w-7xl mx-auto">
        <main>{appState === 'landing' ? renderLandingPage() : renderProcessingPage()}</main>
      </div>
    </div>
  );
};

export default App;
