import React from 'react';
import { useDomainStore } from '@/store';
import { Plug, ChevronDown } from 'lucide-react';

export const StationOverview: React.FC = () => {
  const [isMinimized, setIsMinimized] = React.useState(true);
  const stations = useDomainStore(state => state.systemState?.stations);

  if (!stations || stations.length === 0) return null;

  const activeStations = stations.filter(s => s.occupancy).length;

  return (
    <div className={`bg-white dark:bg-black border border-zinc-200 dark:border-zinc-800 shadow-sm pointer-events-auto transition-all duration-300 ${isMinimized ? 'rounded-full' : 'rounded-2xl'}`}>
      {/* Header Pill */}
      <div 
        className="flex items-center justify-between p-2.5 px-4 cursor-pointer hover:bg-zinc-50 dark:hover:bg-zinc-900 transition-colors rounded-full"
        onClick={() => setIsMinimized(!isMinimized)}
      >
        <div className="flex items-center gap-3 text-black dark:text-white uppercase tracking-wider text-xs">
          <Plug size={16} className="text-black dark:text-white" />
          <span className="font-bold">Stations <span className="text-zinc-300 dark:text-zinc-600 mx-1">•</span> {activeStations}/{stations.length} <span className="text-zinc-500 font-semibold lowercase">in use</span></span>
        </div>
        <ChevronDown size={16} className={`text-zinc-400 transition-transform duration-300 ${isMinimized ? '' : 'rotate-180'}`} />
      </div>

      {/* Expandable Content */}
      <div className={`grid transition-[grid-template-rows] duration-300 ${isMinimized ? 'grid-rows-[0fr]' : 'grid-rows-[1fr]'}`}>
        <div className="overflow-hidden">
          <div className="p-4 pt-2 border-t border-zinc-100 dark:border-zinc-800 space-y-3">
            <div className="flex flex-col gap-2">
              {stations.map(station => (
                <div 
                  key={station.station_id} 
                  className="px-3 py-2 bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-lg flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className="text-xs uppercase tracking-wider text-black dark:text-white font-bold w-8">{station.station_id}</div>
                    <div className={`w-2 h-2 rounded-full ${station.occupancy ? 'bg-blue-600' : 'bg-zinc-300 dark:bg-zinc-700'}`} />
                    <div className="text-[10px] uppercase font-bold text-zinc-500">
                      {station.status || 'AVAILABLE'}
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {station.occupancy && station.connected_ev_id ? (
                      <div className="text-[10px] font-bold text-blue-600 dark:text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">
                        {station.connected_ev_id}
                      </div>
                    ) : (
                      <div className="text-[10px] font-bold text-zinc-400 uppercase">
                        EMPTY
                      </div>
                    )}
                    <div className="text-[10px] text-zinc-500 font-bold w-10 text-right">
                      {station.maximum_charging_rate} kW
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
