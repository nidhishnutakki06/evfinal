import React from 'react';
import * as THREE from 'three';

export const PowerWires: React.FC = () => {
  // Static structural representation of wires.
  // No flow animation or quantitative changes derived from domain state.
  
  const gridPos = new THREE.Vector3(-25, 1.5, -15);
  const buildingPos = new THREE.Vector3(10, 4, -10);
  const chargingAreaPos = new THREE.Vector3(0, 3, 0);

  return (
    <group>
      {/* Grid to Building */}
      <mesh>
        <tubeGeometry args={[new THREE.LineCurve3(gridPos, buildingPos), 20, 0.05, 8, false]} />
        <meshStandardMaterial color="#444444" />
      </mesh>
      
      {/* Grid to Charging Area */}
      <mesh>
        <tubeGeometry args={[new THREE.LineCurve3(gridPos, chargingAreaPos), 20, 0.05, 8, false]} />
        <meshStandardMaterial color="#444444" />
      </mesh>
    </group>
  );
};
