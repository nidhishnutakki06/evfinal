import React from 'react';
import type { EV } from '@/types/system.types';
import { Battery, Zap, Clock, Target } from 'lucide-react';
import { useDomainStore } from '@/store';
import { A2ExplanationBox } from './A2ExplanationBox';
import { A3ProjectionBar } from './A3ProjectionBar';

interface EVRowProps {
  ev: EV;
}

export const EVRow: React.FC<EVRowProps> = ({ ev }) => {
  const allocations = useDomainStore(state => state.systemState?.allocations) || [];
  const allocation = allocations.find(a => a.ev_id === ev.ev_id);
  const allocationStatus = allocation?.allocation_status?.toUpperCase() || 'NO_ALLOCATION';

  // Base neutral presentation
  let statusColor = 'border-zinc-700 bg-zinc-800/50';

  // Use the authoritative backend field for colors, if it matches semantic keywords, otherwise neutral.
  // We DO NOT infer these states from rates or deadlines.
  if (allocationStatus === 'PAUSED') {
    statusColor = 'border-red-500/50 bg-red-500/10';
  } else if (allocationStatus === 'REDUCED') {
    statusColor = 'border-yellow-500/50 bg-yellow-500/10';
  } else if (allocationStatus === 'ACTIVE' || allocationStatus === 'NORMAL') {
    statusColor = 'border-green-500/50 bg-green-500/10';
  }

  // A3 predictive risk overlay logic
  const hasRisk = ev.a3_risk && ev.a3_risk !== 'NONE';

  return (
    <div className={`p-4 rounded-xl border ${statusColor} relative overflow-hidden transition-all duration-300`}>
      {hasRisk && (
        <div className="absolute top-0 right-0 left-0 h-1 bg-amber-500" />
      )}
      
      <div className="flex justify-between items-start mb-3">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h3 className="font-bold text-zinc-100">{ev.ev_id}</h3>
            
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-sm uppercase tracking-wide 
              ${allocationStatus === 'PAUSED' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
              allocationStatus === 'ACTIVE' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' : 
              allocationStatus === 'REDUCED' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 
              'bg-zinc-700 text-zinc-400'}`}>
              Alloc: {allocationStatus}
            </span>
          </div>
          <p className="text-xs text-zinc-400 mt-1">{ev.vehicle_type} | Station {ev.station_id || 'N/A'}</p>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold text-zinc-100">{ev.current_rate?.toFixed(1) ?? '0.0'} kW</div>
          <div className="text-xs text-blue-400 mt-1">Solar Contrib: {ev.solar_contribution?.toFixed(1) ?? '0.0'} kW</div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mt-4 bg-zinc-900/50 p-3 rounded-lg">
        <div>
          <div className="text-xs text-zinc-500 flex items-center gap-1 mb-1"><Battery size={12} /> SoC</div>
          <div className="text-sm font-semibold text-zinc-200">{ev.current_soc.toFixed(1)}% / {ev.target_soc.toFixed(1)}%</div>
        </div>
        <div>
          <div className="text-xs text-zinc-500 flex items-center gap-1 mb-1"><Zap size={12} /> Required</div>
          <div className="text-sm font-semibold text-zinc-200">{ev.energy_required?.toFixed(1) ?? '--'} kWh</div>
        </div>
        <div>
          <div className="text-xs text-zinc-500 flex items-center gap-1 mb-1"><Clock size={12} /> Time Rem.</div>
          <div className="text-sm font-semibold text-zinc-200">{ev.time_remaining?.toFixed(1) ?? '--'} h</div>
        </div>
        <div>
          <div className="text-xs text-zinc-500 flex items-center gap-1 mb-1"><Target size={12} /> Priority</div>
          <div className="text-sm font-semibold text-zinc-200">{ev.priority_score?.toFixed(1) ?? '--'}</div>
        </div>
      </div>
      
      <A3ProjectionBar ev={ev} />
      <A2ExplanationBox ev={ev} allocation={allocation} />
    </div>
  );
};
