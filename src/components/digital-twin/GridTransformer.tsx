import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { useDomainStore } from '@/store';
import * as THREE from 'three';

interface GridTransformerProps {
  onSelect: (id: string, type: string) => void;
}

export const GridTransformer: React.FC<GridTransformerProps> = ({ onSelect }) => {
  const isEmergency = useDomainStore(state => state.systemState?.emergency?.emergency_active_state);
  const materialRef = useRef<THREE.MeshStandardMaterial>(null);

  useFrame((state) => {
    if (materialRef.current) {
      if (isEmergency) {
        const pulse = (Math.sin(state.clock.elapsedTime * 4) + 1) / 2;
        materialRef.current.emissive.setHex(0xff0000);
        materialRef.current.emissiveIntensity = 0.5 + pulse * 0.5;
        materialRef.current.color.setHex(0x550000);
      } else {
        materialRef.current.emissive.setHex(0x000000);
        materialRef.current.emissiveIntensity = 0;
        materialRef.current.color.setHex(0x7f8c8d);
      }
    }
  });

  return (
    <group position={[-25, 1, -15]} onClick={(e: any) => { e.stopPropagation(); onSelect('Grid', 'GRID'); }}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[4, 2, 4]} />
        <meshStandardMaterial ref={materialRef} color="#7f8c8d" metalness={0.8} roughness={0.2} />
      </mesh>
      <mesh position={[0, 1.25, 0]} castShadow>
        <cylinderGeometry args={[0.5, 0.5, 0.5, 16]} />
        <meshStandardMaterial color="#95a5a6" metalness={0.9} />
      </mesh>
    </group>
  );
};
