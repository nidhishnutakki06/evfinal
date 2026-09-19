import React from 'react';
import { useDomainStore } from '@/store';
import { MetricCard } from './MetricCard';
import { Sun, ChevronDown } from 'lucide-react';

export const SolarMetrics: React.FC = () => {
  const [isMinimized, setIsMinimized] = React.useState(true);
  const solar = useDomainStore(state => state.systemState?.solar);

  if (!solar) return null;

  return (
    <div className={`bg-white dark:bg-black border border-zinc-200 dark:border-zinc-800 shadow-sm pointer-events-auto transition-all duration-300 ${isMinimized ? 'rounded-full' : 'rounded-2xl'}`}>
      {/* Header Pill */}
      <div 
        className="flex items-center justify-between p-2.5 px-4 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors rounded-full"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className="flex items-center gap-3 text-black dark:text-white uppercase tracking-wider text-xs">
          <Sun size={16} className="text-black dark:text-white" />
          <span className="font-bold">Solar <span className="text-zinc-300 dark:text-zinc-600 mx-1">•</span> {solar.generation?.toFixed(1) ?? '--'} <span className="text-zinc-500 font-semibold">kW</span></span>
        </div>
        <ChevronDown size={16} className={`text-zinc-400 transition-transform duration-300 ${isMinimized ? '' : 'rotate-180'}`} />
      </div>

      {/* Expandable Content */}
      <div className={`grid transition-[grid-template-rows] duration-300 ${isMinimized ? 'grid-rows-[0fr]' : 'grid-rows-[1fr]'}`}>
        <div className="overflow-hidden">
          <div className="p-4 pt-2 border-t border-zinc-100 dark:border-zinc-800">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <MetricCard
                title="Generation"
                value={solar.generation?.toFixed(1) ?? '--'}
                unit="kW"
                statusColor="neutral"
              />
              <MetricCard
                title="Usable Solar"
                value={solar.usable_solar?.toFixed(1) ?? '--'}
                unit="kW"
                statusColor="green"
                highlight
              />
              <MetricCard
                title="Excess Solar"
                value={solar.excess_solar?.toFixed(1) ?? '--'}
                unit="kW"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
