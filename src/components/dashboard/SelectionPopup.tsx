import React from 'react';
import { useDomainStore } from '@/store';
import { SelectionState, useSelection } from '@/state/SelectionStore';
import { X } from 'lucide-react';
import { A2ExplanationBox } from './A2ExplanationBox';
import { A3ProjectionBar } from './A3ProjectionBar';

export const SelectionPopup: React.FC = () => {
  const selection = useSelection();
  const systemState = useDomainStore(state => state.systemState);
  
  if (!selection.type || !selection.id || !systemState) return null;

  let content = null;
  const entityId = selection.id;
  let title = entityId;

  if (selection.type === 'ev') {
    const ev = systemState.evs?.find(e => e.ev_id === entityId);
    if (ev) {
      const alloc = systemState.allocations?.find(a => a.ev_id === ev.ev_id);
      content = (
        <div className="space-y-2 text-sm text-slate-700 dark:text-zinc-300">
          <p><strong>Type:</strong> {ev.vehicle_type}</p>
          <p><strong>SoC:</strong> {ev.current_soc?.toFixed(1)}% / {ev.target_soc?.toFixed(1)}%</p>
          <p><strong>Station:</strong> {ev.station_id || 'None'}</p>
          <p><strong>Expected Range:</strong> {ev.range?.toFixed(1)} km</p>
          <p><strong>Arrival:</strong> {ev.arrival?.toFixed(1) || '--'}h | <strong>Departure:</strong> {ev.departure?.toFixed(1) || '--'}h</p>
          {alloc && (
            <>
              <p><strong>Allocation:</strong> {alloc.allocation_status}</p>
              <p><strong>Current Rate:</strong> {alloc.allocated_rate?.toFixed(1)} kW</p>
              <p><strong>Solar Contrib:</strong> {alloc.solar_contribution?.toFixed(1)} kW</p>
            </>
          )}
          {ev.priority_score !== undefined && (
            <p><strong>Priority Score:</strong> {ev.priority_score?.toFixed(2)}</p>
          )}
          <A3ProjectionBar ev={ev} />
          <A2ExplanationBox ev={ev} allocation={alloc} />
        </div>
      );
    }
  } else if (selection.type === 'station') {
    const station = systemState.stations?.find(s => s.station_id === entityId);
    if (station) {
      content = (
        <div className="space-y-2 text-sm text-slate-700 dark:text-zinc-300">
          <p><strong>Status:</strong> {station.status}</p>
          <p><strong>Occupancy:</strong> {station.occupancy ? 'Yes' : 'No'}</p>
          <p><strong>Connected EV:</strong> {station.connected_ev_id || 'None'}</p>
          <p><strong>Allocated Power:</strong> {station.allocated_power?.toFixed(1) || '0.0'} kW</p>
          <p><strong>Max Rate:</strong> {station.maximum_charging_rate} kW</p>
        </div>
      );
    }
  } else if (selection.type === 'grid') {
    title = 'Grid Infrastructure';
    content = (
      <div className="space-y-2 text-sm text-slate-700 dark:text-zinc-300">
        <p><strong>Import:</strong> {systemState.grid?.grid_import?.toFixed(1)} kW</p>
        <p><strong>Limit:</strong> {systemState.grid?.active_limit?.toFixed(1)} kW</p>
        <p><strong>Safety State:</strong> {systemState.grid?.safety_state}</p>
      </div>
    );
  } else if (selection.type === 'building') {
    title = 'Building Infrastructure';
    content = (
      <div className="space-y-2 text-sm text-slate-700 dark:text-zinc-300">
        <p><strong>Total Demand:</strong> {systemState.building?.total_building_demand?.toFixed(1)} kW</p>
      </div>
    );
  } else if (selection.type === 'solar') {
    title = 'Solar Infrastructure';
    content = (
      <div className="space-y-2 text-sm text-zinc-700 dark:text-zinc-300">
        <p><strong>Generation:</strong> {systemState.solar?.generation?.toFixed(1)} kW</p>
      </div>
    );
  }

  const onClose = () => {
    SelectionState.clear();
  };

  return (
    <div className="absolute top-24 left-1/2 -translate-x-1/2 w-[90%] md:w-80 bg-white dark:bg-black border border-zinc-200 dark:border-zinc-800 p-4 rounded-xl shadow-lg z-20 pointer-events-auto transition-all duration-300">
      <div className="flex justify-between items-start mb-3 border-b border-zinc-100 dark:border-zinc-800 pb-2">
        <h3 className="font-bold text-black dark:text-white uppercase tracking-wider text-sm">{title}</h3>
        <button onClick={onClose} className="text-zinc-400 hover:text-black dark:hover:text-white transition-colors p-1 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-900">
          <X size={16} />
        </button>
      </div>
      {content || <div className="text-sm text-slate-500 dark:text-zinc-500">Entity data unavailable</div>}
    </div>
  );
};
