import React from 'react';
import type { Station } from '@/types/system.types';

interface ChargingStationProps {
  station: Station;
  position: [number, number, number];
  onSelect: (id: string, type: string) => void;
}

export const ChargingStation: React.FC<ChargingStationProps> = ({ station, position, onSelect }) => {
  return (
    <group position={position} onClick={(e: any) => { e.stopPropagation(); onSelect(station.station_id, 'STATION'); }}>
      {/* Base */}
      <mesh castShadow receiveShadow position={[0, 0.5, 0]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial color="#34495e" roughness={0.7} />
      </mesh>
      {/* Pillar */}
      <mesh castShadow position={[0, 1.5, 0]}>
        <boxGeometry args={[0.6, 1.5, 0.6]} />
        <meshStandardMaterial color="#7f8c8d" />
      </mesh>
      {/* Screen/UI face */}
      <mesh position={[0, 1.8, 0.31]}>
        <planeGeometry args={[0.4, 0.6]} />
        <meshStandardMaterial color="#000000" emissive="#1abc9c" emissiveIntensity={station.occupancy ? 0.5 : 0.1} />
      </mesh>
    </group>
  );
};
