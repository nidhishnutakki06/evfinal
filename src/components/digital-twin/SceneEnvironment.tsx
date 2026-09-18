import React from 'react';
import { useDomainStore } from '@/store';
import { Sky } from '@react-three/drei';
import * as THREE from 'three';

export const SceneEnvironment: React.FC = () => {
  const env = useDomainStore(state => state.systemState?.environment);
  const simTime = useDomainStore(state => state.systemState?.simulation?.simulation_time) || 0;

  // Simple sun position calculation based on 24h simulation time
  // e.g. T=12 -> Sun high. T=6 -> Sunrise. T=18 -> Sunset.
  const hour = (simTime % 24);
  const angle = (hour / 24) * Math.PI * 2 - Math.PI / 2;
  
  const sunPosition = new THREE.Vector3(
    Math.cos(angle) * 100,
    Math.max(Math.sin(angle) * 100, -10), // Prevent sun from going too far below horizon
    0
  );

  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight
        position={sunPosition}
        intensity={Math.max(0.1, Math.sin(angle) * 1.5)}
        castShadow
        shadow-mapSize={[1024, 1024]}
      >
        <orthographicCamera attach="shadow-camera" args={[-20, 20, 20, -20, 0.5, 200]} />
      </directionalLight>
      <Sky sunPosition={sunPosition} turbidity={env?.weather === 'CLOUDY' ? 10 : 2} rayleigh={2} />
    </>
  );
};
