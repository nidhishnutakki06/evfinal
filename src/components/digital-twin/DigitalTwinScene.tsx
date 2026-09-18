import React, { useState, Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import { SceneEnvironment } from './SceneEnvironment';
import { SiteGround } from './SiteGround';
import { MainBuilding } from './MainBuilding';
import { GridTransformer } from './GridTransformer';
import { SolarArray } from './SolarArray';
import { StationGroup } from './StationGroup';
import { EVGroup } from './EVGroup';
import { PowerWires } from './PowerWires';
import { SelectionPanel } from './SelectionPanel';

export const DigitalTwinScene: React.FC = () => {
  const [selectedEntityId, setSelectedEntityId] = useState<string | null>(null);
  const [selectedEntityType, setSelectedEntityType] = useState<string | null>(null);

  const handleSelect = (id: string, type: string) => {
    setSelectedEntityId(id);
    setSelectedEntityType(type);
  };

  const handleClosePanel = () => {
    setSelectedEntityId(null);
    setSelectedEntityType(null);
  };

  return (
    <div className="fixed inset-0 w-full h-screen z-0 bg-zinc-950 overflow-hidden pointer-events-auto">
      <SelectionPanel 
        entityId={selectedEntityId} 
        entityType={selectedEntityType} 
        onClose={handleClosePanel} 
      />
      
      <Canvas shadows camera={{ position: [0, 15, 30], fov: 45 }}>
        <Suspense fallback={null}>
          <SceneEnvironment />
          <SiteGround />
          <GridTransformer onSelect={handleSelect} />
          <MainBuilding onSelect={handleSelect} />
          <SolarArray onSelect={handleSelect} />
          <PowerWires />
          <StationGroup onSelect={handleSelect} />
          <EVGroup onSelect={handleSelect} />
          
          <OrbitControls 
            makeDefault 
            maxPolarAngle={Math.PI / 2 - 0.05} // Keep camera above ground
            minDistance={5}
            maxDistance={100}
            target={[0, 0, 0]}
          />
        </Suspense>
      </Canvas>
    </div>
  );
};
