import React from 'react';
import { useDomainStore } from '@/store';

interface SolarArrayProps {
  onSelect: (id: string, type: string) => void;
}

export const SolarArray: React.FC<SolarArrayProps> = ({ onSelect }) => {
  const solar = useDomainStore(state => state.systemState?.solar);
  
  // Neutral presentation of generation. Not used for semantic contribution indicating.
  const isGenerating = solar && (solar.generation ?? 0) > 0;
  
  return (
    <group position={[15, 4.2, -10]} rotation={[0.2, 0, 0]} onClick={(e: any) => { e.stopPropagation(); onSelect('Solar', 'SOLAR'); }}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[8, 0.1, 12]} />
        <meshStandardMaterial 
          color="#2980b9" 
          emissive="#2980b9" 
          emissiveIntensity={isGenerating ? 0.3 : 0} 
          metalness={0.9} 
          roughness={0.1} 
        />
      </mesh>
    </group>
  );
};
