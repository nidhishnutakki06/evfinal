import React from 'react';

interface MainBuildingProps {
  onSelect: (id: string, type: string) => void;
}

export const MainBuilding: React.FC<MainBuildingProps> = ({ onSelect }) => {
  return (
    <group position={[15, 2, -10]} onClick={(e: any) => { e.stopPropagation(); onSelect('Building', 'BUILDING'); }}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[10, 4, 15]} />
        <meshStandardMaterial color="#2c3e50" roughness={0.6} metalness={0.2} />
      </mesh>
      {/* Visual only windows, static presentation */}
      <mesh position={[-5.1, 0, 0]} castShadow>
        <boxGeometry args={[0.2, 2, 10]} />
        <meshStandardMaterial color="#3498db" emissive="#3498db" emissiveIntensity={0.2} />
      </mesh>
    </group>
  );
};
