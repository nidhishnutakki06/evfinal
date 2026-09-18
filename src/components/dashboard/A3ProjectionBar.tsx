import React from 'react';
import type { EV } from '@/types/system.types';
import { AlertTriangle } from 'lucide-react';

interface A3ProjectionBarProps {
  ev: EV;
}

export const A3ProjectionBar: React.FC<A3ProjectionBarProps> = ({ ev }) => {
  const baseSoc = ev.current_soc ?? 0;
  const targetSoc = ev.target_soc ?? 100;
  let projectedSoc = baseSoc;

  // Exact 30-minute deterministic projection relying on current rate
  if (ev.current_rate && ev.battery_capacity && ev.battery_capacity > 0) {
    const energyAddedKwh = ev.current_rate * 0.5; // current_rate (kW) * 0.5 hours (30 mins)
    const socAddedPercent = (energyAddedKwh / ev.battery_capacity) * 100;
    
    if (baseSoc < targetSoc) {
      const maxGain = targetSoc - baseSoc;
      projectedSoc = baseSoc + Math.min(maxGain, socAddedPercent);
    }
    // If baseSoc >= targetSoc, no additional charge is projected (capped safely).
  }

  // Risk remains entirely backend-authoritative
  const hasRisk = ev.a3_risk && ev.a3_risk !== 'NONE';

  return (
    <div className="mt-2 bg-zinc-950/50 border border-zinc-800/80 rounded-lg p-3 text-xs">
      <div className="flex items-center justify-between mb-2">
        <div className="font-semibold text-zinc-300 uppercase tracking-wider text-[10px]">30-Minute Projection</div>
        {hasRisk && (
          <div className="flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-sm uppercase tracking-wide bg-amber-500/20 text-amber-500 border border-amber-500/30">
            <AlertTriangle size={10} /> Predictive Risk: {ev.a3_risk}
          </div>
        )}
      </div>

      <div className="flex justify-between text-zinc-400 mb-1 text-[10px]">
        <span>Current: {baseSoc.toFixed(1)}%</span>
        <span>Projected: {projectedSoc.toFixed(1)}%</span>
        <span>Target: {targetSoc.toFixed(1)}%</span>
      </div>

      <div className="relative w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
        {/* Target marker */}
        <div 
          className="absolute top-0 bottom-0 w-0.5 bg-zinc-400 z-30"
          style={{ left: `${Math.min(100, Math.max(0, targetSoc))}%` }}
        />
        
        {/* Projected fill */}
        <div 
          className="absolute top-0 bottom-0 left-0 bg-blue-500/40 transition-all duration-300 z-10"
          style={{ width: `${Math.min(100, Math.max(0, projectedSoc))}%` }}
        />
        
        {/* Current fill */}
        <div 
          className="absolute top-0 bottom-0 left-0 bg-blue-500 transition-all duration-300 z-20"
          style={{ width: `${Math.min(100, Math.max(0, baseSoc))}%` }}
        />
      </div>
    </div>
  );
};
