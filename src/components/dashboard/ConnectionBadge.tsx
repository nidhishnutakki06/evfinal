import React from 'react';
import { useDomainStore } from '@/store';
import { Wifi, WifiOff, Loader2, Activity } from 'lucide-react';
import { env } from '@/config/env';

export const ConnectionBadge: React.FC = () => {
  const connectionStatus = useDomainStore(state => state.connectionStatus);

  if (env.IS_DEV_PREVIEW) {
    return (
      <div className="flex items-center space-x-2 text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full text-sm font-medium border border-purple-500/20">
        <Activity size={14} />
        <span>DEV PREVIEW</span>
      </div>
    );
  }

  if (connectionStatus === 'connected') {
    return (
      <div className="flex items-center space-x-2 text-green-500 bg-green-500/10 px-3 py-1 rounded-full text-sm font-medium border border-green-500/20">
        <Wifi size={14} />
        <span>Live</span>
      </div>
    );
  }

  if (connectionStatus === 'connecting' || connectionStatus === 'error') {
    return (
      <div className="flex items-center space-x-2 text-yellow-500 bg-yellow-500/10 px-3 py-1 rounded-full text-sm font-medium border border-yellow-500/20">
        <Loader2 size={14} className="animate-spin" />
        <span>Reconnecting...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 text-red-500 bg-red-500/10 px-3 py-1 rounded-full text-sm font-medium border border-red-500/20">
      <WifiOff size={14} />
      <span>Disconnected</span>
    </div>
  );
};
