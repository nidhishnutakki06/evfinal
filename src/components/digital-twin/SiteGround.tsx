import React from 'react';

export const SiteGround: React.FC = () => {
  return (
    <group>
      {/* Main Ground */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[0, -0.1, 0]}>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial color="#1a1a1a" roughness={0.8} />
      </mesh>
      
      {/* Parking Area Visual Demarcation */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[0, 0, 0]}>
        <planeGeometry args={[30, 20]} />
        <meshStandardMaterial color="#222222" roughness={0.9} />
      </mesh>

      {/* Grid Area Demarcation */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} receiveShadow position={[-25, 0, -15]}>
        <planeGeometry args={[10, 10]} />
        <meshStandardMaterial color="#2a2a2a" roughness={0.7} />
      </mesh>
    </group>
  );
};
