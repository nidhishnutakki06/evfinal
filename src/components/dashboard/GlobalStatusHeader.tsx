import React from 'react';
import { useDomainStore } from '@/store';
import { ConnectionBadge } from './ConnectionBadge';
import { Clock, Sun, ShieldAlert, Activity } from 'lucide-react';
import { SimulationLifecycleControl } from './controls/SimulationLifecycleControl';

export const GlobalStatusHeader: React.FC = () => {
  const systemState = useDomainStore(state => state.systemState);

  return (
    <header className="flex flex-col md:flex-row justify-between items-start md:items-center p-2 md:px-5 md:py-2.5 bg-white dark:bg-black border border-zinc-200 dark:border-zinc-800 space-y-4 md:space-y-0 shadow-sm rounded-full mx-auto mt-4 w-fit max-w-full pointer-events-auto transition-all duration-300">
      <div className="flex items-center space-x-6 mr-6">
        <h1 className="text-sm font-bold tracking-tight text-black dark:text-white flex items-center gap-2 uppercase">
          <Activity className="text-black dark:text-white w-4 h-4" />
          SH-305 Operations
        </h1>
        <ConnectionBadge />
      </div>

      {systemState && (
        <div className="flex flex-wrap items-center gap-2 text-xs font-bold uppercase tracking-wider">
          <div className="flex items-center space-x-2 text-black dark:text-white bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 px-3 py-1 rounded-full">
            <Clock size={14} className="text-zinc-500" />
            <span>T+{systemState.simulation?.simulation_time?.toFixed(1) ?? '0.0'}h</span>
            <span className={systemState.simulation?.is_running ? "text-black dark:text-white" : "text-red-600"}>
              {systemState.simulation?.is_running ? 'RUNNING' : 'PAUSED'}
            </span>
            <SimulationLifecycleControl />
          </div>

          <div className="flex items-center space-x-2 text-black dark:text-white bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 px-3 py-1 rounded-full">
            <Sun size={14} className="text-zinc-500" />
            <span>{systemState.environment?.weather ?? '--'} • {systemState.environment?.time_of_day ?? '--'}</span>
          </div>

          <div className="flex items-center space-x-2 text-black dark:text-white bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 px-3 py-1 rounded-full">
            <span className="text-zinc-500">STRATEGY:</span>
            <span>{systemState.strategy?.active_strategy?.replace(/_/g, ' ') ?? 'N/A'}</span>
          </div>

          {systemState.emergency?.emergency_active_state && (
            <div className="flex items-center space-x-2 text-white bg-red-600 px-3 py-1 rounded-full border border-red-700 animate-pulse">
              <ShieldAlert size={14} />
              <span>EMERGENCY ACTIVE</span>
            </div>
          )}
        </div>
      )}
    </header>
  );
};
