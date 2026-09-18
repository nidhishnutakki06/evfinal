import React, { useState } from 'react';
import { useDomainStore } from '@/store';
import { controlsApi } from '@/services/api/controls';
import type { StrategyType } from '@/types/system.types';
import { Target, Sun, ShieldAlert, Loader2, GitMerge, ChevronDown } from 'lucide-react';

const strategies: { value: StrategyType, label: string, icon: React.FC<any> }[] = [
  { value: 'DEADLINE_FIRST', label: 'Deadline First', icon: Target },
  { value: 'SOLAR_FIRST', label: 'Solar First', icon: Sun },
  { value: 'GRID_SAFETY_FIRST', label: 'Grid Safety First', icon: ShieldAlert },
];

export const A4StrategyControl: React.FC = () => {
  const [isMinimized, setIsMinimized] = useState(true);
  const systemState = useDomainStore(state => state.systemState);
  const activeStrategy = systemState?.strategy?.active_strategy;
  
  const [pendingStrategy, setPendingStrategy] = useState<StrategyType | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleStrategyChange = async (strategy: StrategyType) => {
    if (strategy === activeStrategy) return;
    
    setPendingStrategy(strategy);
    setError(null);
    try {
      await controlsApi.setStrategy({ active_strategy: strategy });
      // HTTP success = Command Sent. UI now passively awaits the canonical WebSocket broadcast
      // to update systemState.strategy.active_strategy.
    } catch (err: any) {
      setError(err.message || 'Failed to switch strategy');
    } finally {
      setPendingStrategy(null);
    }
  };

  return (
    <div className={`bg-white dark:bg-black border border-zinc-200 dark:border-zinc-800 shadow-sm w-full md:w-auto pointer-events-auto transition-all duration-300 ${isMinimized ? 'rounded-full' : 'rounded-2xl'}`}>
      {/* Header Pill */}
      <div 
        className="flex items-center justify-between p-2.5 px-4 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors rounded-full"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className="flex items-center gap-3 text-black dark:text-white uppercase tracking-wider text-xs">
          <GitMerge size={16} className="text-black dark:text-white" />
          <span className="font-bold">Strategy <span className="text-zinc-300 dark:text-zinc-600 mx-1">•</span> {activeStrategy?.replace('_', ' ') || 'NONE'}</span>
        </div>
        <ChevronDown size={16} className={`text-zinc-400 transition-transform duration-300 ${isMinimized ? '' : 'rotate-180'}`} />
      </div>

      {/* Expandable Content */}
      <div className={`grid transition-[grid-template-rows] duration-300 ${isMinimized ? 'grid-rows-[0fr]' : 'grid-rows-[1fr]'}`}>
        <div className="overflow-hidden">
          <div className="p-4 pt-2 border-t border-zinc-100 dark:border-zinc-800">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {strategies.map(({ value, label, icon: Icon }) => {
                const isActive = activeStrategy === value;
                const isPending = pendingStrategy === value;
                
                return (
                  <button
                    key={value}
                    onClick={() => handleStrategyChange(value)}
                    disabled={isActive || pendingStrategy !== null}
                    className={`flex flex-col items-center justify-center p-3 rounded-xl border transition-all ${
                      isActive 
                        ? 'bg-black dark:bg-white border-black dark:border-white text-white dark:text-black cursor-default'
                        : 'bg-zinc-50 dark:bg-zinc-900 border-zinc-200 dark:border-zinc-800 text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800'
                    } ${isPending ? 'opacity-70 cursor-not-allowed' : ''}`}
                  >
                    {isPending ? (
                      <Loader2 className={`w-5 h-5 mb-2 animate-spin ${isActive ? 'text-white dark:text-black' : 'text-zinc-500'}`} />
                    ) : (
                      <Icon className={`w-5 h-5 mb-2 ${isActive ? 'text-white dark:text-black' : 'text-zinc-400'}`} />
                    )}
                    <span className="text-[10px] uppercase font-bold tracking-wider text-center leading-tight">{label}</span>
                  </button>
                );
              })}
            </div>
            
            {error && (
              <div className="mt-3 text-[10px] font-bold text-red-600 dark:text-red-400 text-center uppercase tracking-wider">{error}</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
