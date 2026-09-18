import React, { useState } from 'react';
import { useDomainStore } from '@/store';
import { controlsApi } from '@/services/api/controls';
import { Play, Pause, RotateCcw, Loader2 } from 'lucide-react';

export const SimulationLifecycleControl: React.FC = () => {
  const systemState = useDomainStore(state => state.systemState);
  const isRunning = systemState?.simulation?.is_running;
  
  const [pendingAction, setPendingAction] = useState<'start' | 'pause' | 'reset' | null>(null);

  const handleAction = async (action: 'start' | 'pause' | 'reset') => {
    if (pendingAction) return;
    setPendingAction(action);
    try {
      if (action === 'start') await controlsApi.startSimulation();
      else if (action === 'pause') await controlsApi.pauseSimulation();
      else if (action === 'reset') await controlsApi.resetSimulation();
      // HTTP success = Command Sent. UI strictly waits for canonical WebSocket state.
    } catch (err) {
      console.error(`Failed to ${action} simulation`, err);
    } finally {
      setPendingAction(null);
    }
  };

  if (isRunning === undefined) return null;

  return (
    <div className="flex items-center space-x-1 ml-2 border-l border-zinc-700 pl-2">
      {isRunning ? (
        <button
          onClick={() => handleAction('pause')}
          disabled={!!pendingAction}
          className={`p-1.5 rounded transition-colors ${pendingAction === 'pause' ? 'bg-zinc-700 text-yellow-500/50 cursor-wait' : 'hover:bg-zinc-700 text-yellow-400'}`}
          title="Pause Simulation"
        >
          {pendingAction === 'pause' ? <Loader2 size={16} className="animate-spin" /> : <Pause size={16} />}
        </button>
      ) : (
        <button
          onClick={() => handleAction('start')}
          disabled={!!pendingAction}
          className={`p-1.5 rounded transition-colors ${pendingAction === 'start' ? 'bg-zinc-700 text-green-500/50 cursor-wait' : 'hover:bg-zinc-700 text-green-400'}`}
          title="Start Simulation"
        >
          {pendingAction === 'start' ? <Loader2 size={16} className="animate-spin" /> : <Play size={16} />}
        </button>
      )}

      <button
        onClick={() => handleAction('reset')}
        disabled={!!pendingAction}
        className={`p-1.5 rounded transition-colors ${pendingAction === 'reset' ? 'bg-zinc-700 text-zinc-500/50 cursor-wait' : 'hover:bg-red-500/20 text-red-400'}`}
        title="Reset Simulation"
      >
        {pendingAction === 'reset' ? <Loader2 size={16} className="animate-spin text-red-400" /> : <RotateCcw size={16} />}
      </button>
    </div>
  );
};
