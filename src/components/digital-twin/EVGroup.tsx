import React from 'react';
import { useDomainStore } from '@/store';
import { EVModel } from './EVModel';

interface EVGroupProps {
  onSelect: (id: string, type: string) => void;
}

export const EVGroup: React.FC<EVGroupProps> = ({ onSelect }) => {
  const evs = useDomainStore(state => state.systemState?.evs) || [];
  const stations = useDomainStore(state => state.systemState?.stations) || [];

  return (
    <group position={[0, 0, 5]}>
      {evs.map((ev, index) => {
        // Find position based on assigned station
        const assignedStationIndex = stations.findIndex(s => s.station_id === ev.station_id);
        
        let xPos = 0;
        let zPos = 3; // Parked in front of the station row
        
        if (assignedStationIndex !== -1) {
          xPos = (assignedStationIndex - stations.length / 2) * 4;
        } else {
          // Neutral fallback position for EVs without a valid station assignment
          xPos = (index - evs.length / 2) * 2;
          zPos = 10; 
        }

        return (
          <EVModel 
            key={ev.ev_id}
            ev={ev}
            position={[xPos, 0, zPos]}
            onSelect={onSelect}
          />
        );
      })}
    </group>
  );
};
