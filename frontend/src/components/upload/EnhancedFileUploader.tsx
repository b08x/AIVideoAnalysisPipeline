// src/components/upload/EnhancedFileUploader.tsx
import React, { useState, useRef, useCallback } from 'react';
import { UploadCloudIcon, XIcon, FileTextIcon, FilmIcon, AlertTriangleIcon } from '../Icons';

interface EnhancedFileUploaderProps {
  onFileSelect: (file: File) => void;
  onFileClear: () => void;
  file: File | null;
  title: string;
  acceptedTypes: string;
  validationFn: (file: File) => string | null;
  icon: 'video' | 'subtitle';
}

const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

const FilePreview: React.FC<{ file: File, onClear: () => void, icon: 'video' | 'subtitle' }> = ({ file, onClear, icon }) => (
    <div className="bg-[#0D1117] p-3 rounded-lg border border-brand-border">
        <div className="flex items-center gap-3">
            <div className="flex-shrink-0">
                {icon === 'video' ? <FilmIcon className="w-6 h-6 text-brand-accent"/> : <FileTextIcon className="w-6 h-6 text-brand-accent"/>}
            </div>
            <div className="flex-grow min-w-0">
                <p className="text-sm font-medium text-brand-text-primary truncate" title={file.name}>{file.name}</p>
                <p className="text-xs text-brand-text-secondary">
                    {formatFileSize(file.size)} &bull; {file.type || 'unknown type'}
                </p>
            </div>
            <button onClick={onClear} className="text-brand-text-secondary hover:text-red-500 transition-colors flex-shrink-0">
                <XIcon className="w-5 h-5" />
            </button>
        </div>
    </div>
);

const EnhancedFileUploader: React.FC<EnhancedFileUploaderProps> = ({ onFileSelect, onFileClear, file, title, acceptedTypes, validationFn, icon }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const inputRef = useRef<HTMLInputElement>(null);

    const handleFile = useCallback((selectedFile: File) => {
        const validationError = validationFn(selectedFile);
        if (validationError) {
            setError(validationError);
            onFileClear(); // Clear any previously valid file
        } else {
            setError(null);
            onFileSelect(selectedFile);
        }
    }, [validationFn, onFileSelect, onFileClear]);

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") setIsDragging(true);
        else if (e.type === "dragleave") setIsDragging(false);
    };

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setIsDragging(false);
        if (e.dataTransfer.files?.[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    }, [handleFile]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const clearFile = () => {
        setError(null);
        onFileClear();
        if(inputRef.current) {
            inputRef.current.value = "";
        }
    }

    return (
        <div className="w-full">
            <h3 className="text-lg font-semibold text-brand-text-primary mb-2">{title}</h3>
            {file ? (
                <FilePreview file={file} onClear={clearFile} icon={icon} />
            ) : (
                <div className="flex flex-col">
                    <div
                        onDragEnter={handleDrag} onDragLeave={handleDrag} onDragOver={handleDrag} onDrop={handleDrop}
                        onClick={() => inputRef.current?.click()}
                        className={`flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg cursor-pointer transition-colors
                            ${isDragging ? 'border-brand-accent bg-brand-accent/10' : 'border-brand-border hover:border-brand-accent/70'}`}
                    >
                        <UploadCloudIcon className="w-10 h-10 text-brand-text-secondary mb-2"/>
                        <p className="text-brand-text-secondary text-sm">Drag & drop or <span className="font-semibold text-brand-accent">browse</span></p>
                        <p className="text-xs text-brand-text-secondary mt-1">{acceptedTypes}</p>
                        <input type="file" ref={inputRef} onChange={handleChange} accept={acceptedTypes} className="hidden" />
                    </div>
                    {error && (
                        <div className="flex items-center gap-2 mt-2 text-red-400 text-sm">
                            <AlertTriangleIcon className="w-4 h-4 flex-shrink-0"/>
                            <p>{error}</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default EnhancedFileUploader;
