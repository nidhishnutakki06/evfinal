import React from 'react';
import { BuildingDemandControl } from './BuildingDemandControl';
import { GridLimitControl } from './GridLimitControl';
import { WeatherControl } from './WeatherControl';
import { SpawnEVControl } from './SpawnEVControl';
import { SlidersHorizontal, ChevronDown } from 'lucide-react';

export const WhatIfControlsPanel: React.FC = () => {
  const [isMinimized, setIsMinimized] = React.useState(true);

  return (
    <div className={`flex flex-col bg-white dark:bg-black border border-zinc-200 dark:border-zinc-800 shadow-sm pointer-events-auto transition-all duration-300 ${isMinimized ? 'rounded-full' : 'rounded-2xl'}`}>
      {/* Header Pill */}
      <div 
        className="flex items-center justify-between p-2.5 px-4 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors rounded-full shrink-0"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className="flex items-center gap-3 uppercase tracking-wider text-xs text-black dark:text-white">
          <SlidersHorizontal size={16} className="text-black dark:text-white" />
          <span className="font-bold">A1 Controls</span>
        </div>
        <ChevronDown size={16} className={`text-zinc-400 transition-transform duration-300 ${isMinimized ? '' : 'rotate-180'}`} />
      </div>

      {/* Expandable Content */}
      <div className={`grid transition-[grid-template-rows] duration-300 ${isMinimized ? 'grid-rows-[0fr]' : 'grid-rows-[1fr]'} max-h-[60vh]`}>
        <div className="overflow-hidden flex flex-col min-h-0">
          <div className="p-4 pt-2 border-t border-zinc-100 dark:border-zinc-800 flex-1 overflow-y-auto scrollbar-thin">
            <div className="space-y-4 pr-2">
              <GridLimitControl />
              <BuildingDemandControl />
              <WeatherControl />
              <SpawnEVControl />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
