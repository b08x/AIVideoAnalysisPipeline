// src/components/ServerStatusIndicator.tsx
import React, { useState, useEffect } from 'react';
import { ServerIcon, LoaderIcon } from './Icons';

type Status = 'online' | 'offline' | 'checking';

const ServerStatusIndicator: React.FC = () => {
  const [status, setStatus] = useState<Status>('checking');

  useEffect(() => {
    const checkStatus = async () => {
      try {
        // Connect directly to backend - no proxy
        const response = await fetch('http://localhost:8000/api/v1/health');
        if (response.ok) {
          setStatus('online');
        } else {
          setStatus('offline');
        }
      } catch (error) {
        setStatus('offline');
      }
    };

    // Check status immediately on mount and then every 30 seconds
    checkStatus();
    const intervalId = setInterval(checkStatus, 30000);

    return () => clearInterval(intervalId);
  }, []);

  const statusConfig = {
    online: {
      text: 'Processing Engine: Online',
      color: 'text-green-400',
      icon: <ServerIcon className="w-4 h-4" />,
    },
    offline: {
      text: 'Processing Engine: Offline',
      color: 'text-red-400',
      icon: <ServerIcon className="w-4 h-4" />,
    },
    checking: {
      text: 'Checking Engine Status...',
      color: 'text-yellow-400',
      icon: <LoaderIcon className="w-4 h-4 animate-spin" />,
    },
  };

  const currentStatus = statusConfig[status];

  return (
    <div className={`flex items-center gap-2 text-sm font-medium ${currentStatus.color}`}>
      {currentStatus.icon}
      <span>{currentStatus.text}</span>
    </div>
  );
};

export default ServerStatusIndicator;
