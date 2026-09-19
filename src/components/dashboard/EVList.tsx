import React from 'react';
import { useDomainStore } from '@/store';
import { EVRow } from './EVRow';
import { Car } from 'lucide-react';

export const EVList: React.FC = () => {
  const evs = useDomainStore(state => state.systemState?.evs);

  if (!evs) return null;

  return (
    <div className="space-y-4 h-full flex flex-col bg-zinc-900/90 border border-zinc-700/50 p-4 rounded-2xl shadow-lg">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold text-zinc-200 flex items-center gap-2">
          <Car size={20} className="text-blue-500" /> Active Operations
        </h2>
        <span className="bg-zinc-800 text-zinc-300 text-xs px-2 py-1 rounded-md font-medium border border-zinc-700">
          {evs.length} EVs
        </span>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 space-y-3">
        {evs.length === 0 ? (
          <div className="h-40 flex items-center justify-center text-zinc-500 border border-dashed border-zinc-700 rounded-xl">
            No active EVs in the system
          </div>
        ) : (
          evs.map(ev => <EVRow key={ev.ev_id} ev={ev} />)
        )}
      </div>
    </div>
  );
};
