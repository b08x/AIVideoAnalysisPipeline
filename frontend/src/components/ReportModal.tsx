
import React, { useEffect, useRef } from 'react';
import { XIcon } from './Icons';

// A simple markdown to HTML converter to support headings with IDs, lists, links, and bold text.
const SimpleMarkdown: React.FC<{ content: string }> = ({ content }) => {
    const createSlug = (text: string) => {
        return text
            .toLowerCase()
            .replace(/&/g, 'and')
            .replace(/[\s_]+/g, '-')
            .replace(/[^\w-]+/g, '');
    };

    const lines = content.split('\n');
    let html = '';
    let inList = false;

    const closeList = () => {
        if (inList) {
            html += '</ul>';
            inList = false;
        }
    };

    for (const line of lines) {
        // First, handle inline elements like bold and links.
        let processedLine = line
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-brand-accent hover:underline">$1</a>');
        
        // Now handle block-level elements.
        if (processedLine.startsWith('### ')) {
            closeList();
            const text = processedLine.substring(4);
            html += `<h3 id="${createSlug(text)}" class="text-xl font-bold mt-4 mb-3">${text}</h3>`;
        } else if (processedLine.startsWith('## ')) {
            closeList();
            const text = processedLine.substring(3);
            html += `<h2 id="${createSlug(text)}" class="text-2xl font-bold mt-6 mb-4 border-b border-brand-border pb-2">${text}</h2>`;
        } else if (processedLine.startsWith('# ')) {
            closeList();
            const text = processedLine.substring(2);
            html += `<h1 id="${createSlug(text)}" class="text-3xl font-bold mb-6">${text}</h1>`;
        } else if (processedLine.trim().startsWith('- ')) {
            if (!inList) {
                html += '<ul class="list-disc list-outside ml-4 space-y-1">';
                inList = true;
            }
            const listItemContent = processedLine.trim().substring(2).trim();
            html += `<li>${listItemContent}</li>`;
        } else if (processedLine.trim() === '') {
            closeList();
        } else {
            closeList();
            html += `<p class="my-2">${processedLine}</p>`;
        }
    }

    closeList();

    return <div className="prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: html }} />;
};

interface ReportModalProps {
  report: string;
  onClose: () => void;
}

const ReportModal: React.FC<ReportModalProps> = ({ report, onClose }) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleEsc = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleEsc);

    return () => {
      window.removeEventListener('keydown', handleEsc);
    };
  }, [onClose]);

  if (!report) return null;

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50 p-4"
      onClick={onClose}
    >
      <div 
        ref={modalRef}
        className="bg-brand-surface w-full max-w-4xl h-full max-h-[90vh] rounded-lg shadow-2xl flex flex-col text-brand-text-primary border border-brand-border"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center p-4 border-b border-brand-border flex-shrink-0">
          <h2 className="text-xl font-bold">Generated Analysis Report</h2>
          <button onClick={onClose} className="text-brand-text-secondary hover:text-brand-text-primary">
            <XIcon className="w-6 h-6" />
          </button>
        </div>
        <div className="p-6 overflow-y-auto">
            <SimpleMarkdown content={report} />
        </div>
      </div>
    </div>
  );
};

export default ReportModal;
