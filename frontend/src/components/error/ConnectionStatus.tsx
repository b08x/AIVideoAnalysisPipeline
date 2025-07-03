// src/components/error/ConnectionStatus.tsx
import React, { useState, useEffect } from 'react';
import { AlertTriangleIcon } from '../Icons';

const ConnectionStatus: React.FC = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOnline) {
    return null;
  }

  return (
    <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-yellow-800 text-white text-sm font-semibold px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50 border border-yellow-600">
      <AlertTriangleIcon className="w-5 h-5" />
      You are currently offline. Connection to the server is lost.
    </div>
  );
};

export default ConnectionStatus;
