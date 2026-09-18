import React from 'react';
import type { EV } from '@/types/system.types';
import { useDomainStore } from '@/store';

interface EVModelProps {
  ev: EV;
  position: [number, number, number];
  onSelect: (id: string, type: string) => void;
}

export const EVModel: React.FC<EVModelProps> = ({ ev, position, onSelect }) => {
  // Use authoritative allocation for semantic coloring
  const allocations = useDomainStore(state => state.systemState?.allocations) || [];
  const allocation = allocations.find(a => a.ev_id === ev.ev_id);
  const allocationStatus = allocation?.allocation_status?.toUpperCase();
  
  let baseColor = '#555555';
  
  if (allocationStatus === 'PAUSED') {
    baseColor = '#e74c3c'; // RED
  } else if (allocationStatus === 'REDUCED') {
    baseColor = '#f1c40f'; // YELLOW
  } else if (allocationStatus === 'ACTIVE' || allocationStatus === 'NORMAL') {
    baseColor = '#2ecc71'; // GREEN
  }

  const fillRatio = Math.max(0.01, ev.current_soc / 100);

  return (
    <group position={position} onClick={(e: any) => { e.stopPropagation(); onSelect(ev.ev_id, 'EV'); }}>
      {/* Car Body */}
      <mesh castShadow receiveShadow position={[0, 0.7, 0]}>
        <boxGeometry args={[1.8, 1, 3.8]} />
        <meshStandardMaterial color={baseColor} metalness={0.6} roughness={0.4} />
      </mesh>
      
      {/* Visual Battery Fill Indicator (SoC) */}
      <mesh position={[0, 1.21, 0]} rotation={[-Math.PI/2, 0, 0]}>
        <planeGeometry args={[1, 2 * fillRatio]} />
        <meshStandardMaterial color="#2ecc71" emissive="#2ecc71" emissiveIntensity={0.5} />
      </mesh>

      {/* A3 Risk Amber Overlay Indicator */}
      {ev.a3_risk && ev.a3_risk !== 'NONE' && (
        <mesh position={[0, 1.3, 1.5]}>
          <boxGeometry args={[0.5, 0.1, 0.5]} />
          <meshStandardMaterial color="#f39c12" emissive="#f39c12" emissiveIntensity={0.8} />
        </mesh>
      )}

    </group>
  );
};
