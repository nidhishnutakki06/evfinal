import React, { useState } from 'react';
import { useDomainStore } from '@/store';
import { controlsApi } from '@/services/api/controls';
import { AlertTriangle, ShieldCheck, Loader2, ChevronDown } from 'lucide-react';

export const A5EmergencyControl: React.FC = () => {
  const [isMinimized, setIsMinimized] = useState(true);
  const systemState = useDomainStore(state => state.systemState);
  const isEmergency = systemState?.emergency?.emergency_active_state;
  
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleToggle = async () => {
    setIsPending(true);
    setError(null);
    try {
      if (isEmergency) {
        await controlsApi.restoreEmergency();
      } else {
        await controlsApi.activateEmergency();
      }
      // HTTP success = Command Sent. UI waits for canonical WebSocket state to update.
    } catch (err: any) {
      setError(err.message || 'Failed to toggle emergency state');
    } finally {
      setIsPending(false);
    }
  };

  return (
    <div className={`bg-white dark:bg-black border pointer-events-auto transition-all duration-300 w-full md:w-auto shadow-sm ${
      isEmergency 
        ? `border-red-500/50 ${isMinimized ? '' : 'shadow-[0_0_15px_rgba(239,68,68,0.15)]'}`
        : 'border-zinc-200 dark:border-zinc-800'
    } ${isMinimized ? 'rounded-full' : 'rounded-2xl'}`}>
      
      {/* Header Pill */}
      <div 
        className={`flex items-center justify-between p-2.5 px-4 cursor-pointer transition-colors rounded-full ${
          isEmergency 
            ? 'bg-red-600 hover:bg-red-700 text-white' 
            : 'hover:bg-zinc-50 dark:hover:bg-zinc-900'
        }`}
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className={`flex items-center gap-3 uppercase tracking-wider text-xs ${isEmergency ? '' : 'text-black dark:text-white'}`}>
          {isEmergency ? <AlertTriangle size={16} /> : <ShieldCheck size={16} className="text-black dark:text-white" />}
          <span className="font-bold">{isEmergency ? 'EMERGENCY ACTIVE' : 'Emergency'}</span>
        </div>
        <ChevronDown size={16} className={`${isEmergency ? 'text-red-100' : 'text-zinc-400'} ml-4 transition-transform duration-300 ${isMinimized ? '' : 'rotate-180'}`} />
      </div>

      {/* Expandable Content */}
      <div className={`grid transition-[grid-template-rows] duration-300 ${isMinimized ? 'grid-rows-[0fr]' : 'grid-rows-[1fr]'}`}>
        <div className="overflow-hidden">
          <div className={`p-4 pt-2 border-t ${isEmergency ? 'border-red-500/30' : 'border-zinc-100 dark:border-zinc-800'}`}>
            <button
              onClick={handleToggle}
              disabled={isPending}
              className={`w-full flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-bold transition-all text-xs uppercase tracking-wider ${
                isEmergency
                  ? 'bg-red-600 hover:bg-red-700 text-white shadow-[0_0_15px_rgba(220,38,38,0.4)]'
                  : 'bg-black dark:bg-white text-white dark:text-black hover:opacity-80'
              } ${isPending ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
              {isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : isEmergency ? (
                <><ShieldCheck className="w-4 h-4" /> RESTORE NORMAL GRID</>
              ) : (
                <><AlertTriangle className="w-4 h-4" /> ACTIVATE EMERGENCY</>
              )}
            </button>

            {error && <div className="mt-3 text-[10px] font-bold text-red-600 dark:text-red-400 text-center uppercase tracking-wider">{error}</div>}
          </div>
        </div>
      </div>
    </div>
  );
};
