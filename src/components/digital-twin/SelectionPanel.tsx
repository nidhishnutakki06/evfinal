import React from 'react';
import { useDomainStore } from '@/store';
import { X } from 'lucide-react';
import { A2ExplanationBox } from '../dashboard/A2ExplanationBox';
import { A3ProjectionBar } from '../dashboard/A3ProjectionBar';

interface SelectionPanelProps {
  entityId: string | null;
  entityType: string | null;
  onClose: () => void;
}

export const SelectionPanel: React.FC<SelectionPanelProps> = ({ entityId, entityType, onClose }) => {
  const systemState = useDomainStore(state => state.systemState);

  if (!entityId || !entityType || !systemState) return null;

  let content = null;

  if (entityType === 'EV') {
    const ev = systemState.evs.find(e => e.ev_id === entityId);
    if (ev) {
      const alloc = systemState.allocations?.find(a => a.ev_id === ev.ev_id);
      content = (
        <div className="space-y-2 text-sm text-slate-700 dark:text-zinc-300">
          <p><strong>Type:</strong> {ev.vehicle_type}</p>
          <p><strong>SoC:</strong> {ev.current_soc.toFixed(1)}% / {ev.target_soc.toFixed(1)}%</p>
          <p><strong>Station:</strong> {ev.station_id || 'None'}</p>
          {alloc && (
            <>
              <p><strong>Allocation:</strong> {alloc.allocation_status}</p>
              <p><strong>Solar Contrib:</strong> {alloc.solar_contribution?.toFixed(1)} kW</p>
            </>
          )}
          <A3ProjectionBar ev={ev} />
          <A2ExplanationBox ev={ev} allocation={alloc} />
        </div>
      );
    }
  } else if (entityType === 'STATION') {
    const station = systemState.stations.find(s => s.station_id === entityId);
    if (station) {
      content = (
        <div className="space-y-2 text-sm text-slate-700 dark:text-zinc-300">
          <p><strong>Status:</strong> {station.status}</p>
          <p><strong>Occupancy:</strong> {station.occupancy ? 'Yes' : 'No'}</p>
          <p><strong>Connected EV:</strong> {station.connected_ev_id || 'None'}</p>
          <p><strong>Max Rate:</strong> {station.maximum_charging_rate} kW</p>
        </div>
      );
    }
  } else if (entityType === 'GRID') {
    content = (
      <div className="space-y-2 text-sm text-slate-700 dark:text-zinc-300">
        <p><strong>Import:</strong> {systemState.grid.grid_import?.toFixed(1)} kW</p>
        <p><strong>Limit:</strong> {systemState.grid.active_limit.toFixed(1)} kW</p>
        <p><strong>Safety State:</strong> {systemState.grid.safety_state}</p>
      </div>
    );
  } else if (entityType === 'BUILDING') {
    content = (
      <div className="space-y-2 text-sm text-slate-700 dark:text-zinc-300">
        <p><strong>Total Demand:</strong> {systemState.building.total_building_demand?.toFixed(1)} kW</p>
      </div>
    );
  } else if (entityType === 'SOLAR') {
    content = (
      <div className="space-y-2 text-sm text-zinc-700 dark:text-zinc-300">
        <p><strong>Generation:</strong> {systemState.solar.generation?.toFixed(1)} kW</p>
      </div>
    );
  }

  return (
    <div className="absolute top-24 left-1/2 -translate-x-1/2 w-[90%] md:w-80 bg-white dark:bg-black border border-zinc-200 dark:border-zinc-800 p-4 rounded-xl shadow-lg z-20 pointer-events-auto transition-all duration-300">
      <div className="flex justify-between items-start mb-3 border-b border-zinc-100 dark:border-zinc-800 pb-2">
        <h3 className="font-bold text-black dark:text-white uppercase tracking-wider text-sm">{entityId}</h3>
        <button onClick={onClose} className="text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-1 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-900">
          <X size={16} />
        </button>
      </div>
      {content || <div className="text-sm text-slate-500 dark:text-zinc-500">Entity data unavailable</div>}
    </div>
  );
};
