import React from 'react';
import { useDomainStore } from '@/store';
import { ChargingStation } from './ChargingStation';

interface StationGroupProps {
  onSelect: (id: string, type: string) => void;
}

export const StationGroup: React.FC<StationGroupProps> = ({ onSelect }) => {
  const stations = useDomainStore(state => state.systemState?.stations) || [];

  // Layout stations in a row (or grid depending on count)
  return (
    <group position={[0, 0, 5]}>
      {stations.map((station, index) => (
        <ChargingStation 
          key={station.station_id}
          station={station}
          position={[(index - stations.length / 2) * 4, 0, 0]}
          onSelect={onSelect}
        />
      ))}
    </group>
  );
};
