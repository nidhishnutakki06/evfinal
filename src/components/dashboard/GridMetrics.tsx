import React from 'react';
import { useDomainStore } from '@/store';
import { MetricCard } from './MetricCard';
import { Zap, ShieldAlert, ShieldCheck, ChevronDown } from 'lucide-react';

export const GridMetrics: React.FC = () => {
  const [isMinimized, setIsMinimized] = React.useState(true);
  const grid = useDomainStore(state => state.systemState?.grid);

  if (!grid) return null;

  const isSafe = grid.safety_state === 'SAFE';

  return (
    <div className={`bg-white dark:bg-black border border-zinc-200 dark:border-zinc-800 shadow-sm pointer-events-auto transition-all duration-300 ${isMinimized ? 'rounded-full' : 'rounded-2xl'}`}>
      {/* Header Pill */}
      <div 
        className="flex items-center justify-between p-2.5 px-4 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors rounded-full"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className="flex items-center gap-3 text-black dark:text-white uppercase tracking-wider text-xs">
          <Zap size={16} className="text-black dark:text-white" />
          <span className="font-bold">Grid <span className="text-zinc-300 dark:text-zinc-600 mx-1">•</span> {grid.grid_import?.toFixed(1) ?? '--'} <span className="text-zinc-500 font-semibold">kW</span></span>
          {!isSafe && <ShieldAlert size={14} className="text-red-600 animate-pulse" />}
        </div>
        <ChevronDown size={16} className={`text-zinc-400 transition-transform duration-300 ${isMinimized ? '' : 'rotate-180'}`} />
      </div>

      {/* Expandable Content */}
      <div className={`grid transition-[grid-template-rows] duration-300 ${isMinimized ? 'grid-rows-[0fr]' : 'grid-rows-[1fr]'}`}>
        <div className="overflow-hidden">
          <div className="p-4 pt-2 border-t border-zinc-100 dark:border-zinc-800">
            <div className="grid grid-cols-2 gap-3">
              <MetricCard
                title="Grid Import"
                value={grid.grid_import?.toFixed(1) ?? '--'}
                unit="kW"
                statusColor={!isSafe ? 'red' : 'neutral'}
              />
              <MetricCard
                title="Active Limit"
                value={grid.active_limit.toFixed(1)}
                unit="kW"
                subtitle={`Configured: ${grid.configured_limit.toFixed(1)} kW`}
              />
              <MetricCard
                title="Available Cap"
                value={grid.available_capacity?.toFixed(1) ?? '--'}
                unit="kW"
              />
              <MetricCard
                title="Safety State"
                value={grid.safety_state ?? '--'}
                icon={isSafe ? <ShieldCheck className="text-green-600 dark:text-green-500" /> : <ShieldAlert className="text-red-600 dark:text-red-500" />}
                statusColor={isSafe ? 'green' : 'red'}
                highlight
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
