// src/components/error/ErrorBoundary.tsx
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangleIcon } from '../Icons';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // You can also log the error to an error reporting service here
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-brand-bg flex items-center justify-center p-4 text-brand-text-primary">
          <div className="bg-brand-surface border border-red-500 rounded-lg p-8 max-w-lg text-center shadow-2xl">
            <div className="flex justify-center mb-4">
                <AlertTriangleIcon className="w-12 h-12 text-red-400"/>
            </div>
            <h1 className="text-2xl font-bold text-red-400 mb-2">Something went wrong.</h1>
            <p className="text-brand-text-secondary mb-6">
              The application encountered an unexpected error. Please try refreshing the page.
            </p>
            
            {this.state.error && (
                <pre className="bg-[#0D1117] text-left p-3 rounded-md text-xs text-red-300 overflow-x-auto mb-6">
                    <code>{this.state.error.toString()}</code>
                </pre>
            )}

            <button
              onClick={() => window.location.reload()}
              className="bg-brand-accent text-white font-semibold px-6 py-2 rounded-md hover:bg-blue-500 transition-colors"
            >
              Refresh Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
