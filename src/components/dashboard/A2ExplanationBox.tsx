import React from 'react';
import type { EV, Allocation } from '@/types/system.types';

interface A2ExplanationBoxProps {
  ev: EV;
  allocation?: Allocation;
}

export const A2ExplanationBox: React.FC<A2ExplanationBoxProps> = ({ ev, allocation }) => {
  return (
    <div className="mt-3 bg-zinc-950/50 border border-zinc-800/80 rounded-lg p-3 text-xs">
      <div className="font-semibold text-zinc-300 mb-2 uppercase tracking-wider text-[10px]">Why this state?</div>
      
      <div className="mb-2 text-zinc-200 flex items-center gap-2">
        <span className="font-medium text-zinc-400">Allocation decision:</span>
        <span className="font-bold bg-zinc-800 px-2 py-0.5 rounded text-[10px]">{allocation?.allocation_status || 'PENDING'}</span>
      </div>

      <div className="mb-3 text-zinc-200 italic border-l-2 border-blue-500/50 pl-2 bg-blue-500/5 py-1">
        <span className="font-medium text-zinc-400 not-italic block mb-0.5 text-[10px] uppercase">Backend reason:</span>
        {ev.a2_reason && ev.a2_reason !== 'INIT' ? ev.a2_reason : 'No explanation available from the current system state'}
      </div>

      <div className="space-y-1 border-t border-zinc-800 pt-2">
        <div className="font-medium text-zinc-400 mb-1 text-[10px] uppercase">Decision factors:</div>
        <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 text-zinc-300">
          <div className="flex items-center justify-between bg-zinc-900 px-1.5 py-0.5 rounded"><span className="text-zinc-500">Urgency:</span> <span>{ev.urgency || '--'}</span></div>
          <div className="flex items-center justify-between bg-zinc-900 px-1.5 py-0.5 rounded"><span className="text-zinc-500">Priority score:</span> <span>{ev.priority_score?.toFixed(2) ?? '--'}</span></div>
          <div className="flex items-center justify-between bg-zinc-900 px-1.5 py-0.5 rounded"><span className="text-zinc-500">Deadline status:</span> <span>{ev.deadline_status || '--'}</span></div>
          <div className="flex items-center justify-between bg-zinc-900 px-1.5 py-0.5 rounded"><span className="text-zinc-500">Physical feasible:</span> <span>{ev.physical_feasibility ? 'Yes' : 'No'}</span></div>
          <div className="col-span-2 flex items-center justify-between bg-zinc-900 px-1.5 py-0.5 rounded"><span className="text-zinc-500">Current-allocation feasible:</span> <span>{ev.current_allocation_feasibility ? 'Yes' : 'No'}</span></div>
        </div>
      </div>
    </div>
  );
};
