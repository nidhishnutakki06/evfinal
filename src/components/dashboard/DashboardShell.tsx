import React, { Suspense } from 'react';
import { useDomainStore } from '@/store';
import { GlobalStatusHeader } from './GlobalStatusHeader';
import { GridMetrics } from './GridMetrics';
import { BuildingMetrics } from './BuildingMetrics';
import { SolarMetrics } from './SolarMetrics';
import { StationOverview } from './StationOverview';
import { Loader2 } from 'lucide-react';
import { DigitalTwinErrorBoundary } from '../digital-twin/DigitalTwinErrorBoundary';
import { WhatIfControlsPanel } from './controls/WhatIfControlsPanel';
import { A4StrategyControl } from './controls/A4StrategyControl';
import { A5EmergencyControl } from './controls/A5EmergencyControl';
import { Canvas } from '@react-three/fiber';
import { SelectionState } from '../../state/SelectionStore';

const DigitalTwinScene = React.lazy(() =>
  import('../../scene/DigitalTwinScene').then(module => ({ default: module.DigitalTwinScene }))
);

// Static Canvas configurations to prevent prop reference churn on re-renders
const CAMERA_CONFIG = { position: [25, 18, 35] as [number, number, number], fov: 45, near: 0.5, far: 300 };
const GL_CONFIG = { antialias: true, powerPreference: 'high-performance' as const, logarithmicDepthBuffer: true };
const DPR_CONFIG: [number, number] = [1, 1.5];
const handlePointerMissed = () => SelectionState.clear();
const handleCreated = ({ gl }: { gl: any }) => {
  gl.domElement.addEventListener('webglcontextlost', (e: Event) => {
    e.preventDefault();
    console.warn('WebGL context lost - default prevented for automatic recovery.');
  }, false);
};

// Isolated from DashboardShell's reactive systemState updates
const DigitalTwinCanvas = React.memo(() => (
  <DigitalTwinErrorBoundary>
    <Suspense fallback={
      <div className="w-full h-full flex flex-col items-center justify-center text-zinc-500 bg-zinc-950">
        <Loader2 className="w-8 h-8 animate-spin mb-4 text-blue-500" />
        <p className="text-lg">Loading 3D Environment...</p>
      </div>
    }>
      <Canvas
        shadows
        camera={CAMERA_CONFIG}
        onPointerMissed={handlePointerMissed}
        dpr={DPR_CONFIG}
        gl={GL_CONFIG}
        onCreated={handleCreated}
      >
        <DigitalTwinScene />
      </Canvas>
    </Suspense>
  </DigitalTwinErrorBoundary>
));

export const DashboardShell: React.FC = () => {
  const systemState = useDomainStore(state => state.systemState);

  return (
    <div className="relative w-full h-screen overflow-hidden bg-zinc-950">
      {/* 3D Background Layer - Isolated from reactive state updates */}
      <div className="absolute inset-0 z-0">
        <DigitalTwinCanvas />
      </div>

      {/* Transparent UI Overlay Layer */}
      {!systemState ? (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center text-zinc-500 bg-white dark:bg-black pointer-events-auto">
          <Loader2 className="w-8 h-8 animate-spin text-black dark:text-white mb-4" />
          <p className="text-sm font-bold uppercase tracking-wider text-black dark:text-white">Initializing simulation boundary...</p>
        </div>
      ) : (
        <div className="absolute inset-0 z-10 pointer-events-none flex flex-col justify-between">

          {/* Top HUD */}
          <div className="w-full flex justify-center pointer-events-none">
            <GlobalStatusHeader />
          </div>

          {/* Middle HUD Content */}
          <main className="flex-1 w-full flex justify-between p-4 pointer-events-none overflow-hidden">

            {/* Left HUD: Metrics */}
            <div className="flex flex-col space-y-4 w-full max-w-[280px] pointer-events-none">
              <div className="flex flex-col gap-3">
                <GridMetrics />
                <BuildingMetrics />
                <SolarMetrics />
                <StationOverview />
              </div>
            </div>

            {/* Right HUD: Operations */}
            <div className="flex flex-col space-y-4 w-full max-w-[280px] pointer-events-none items-end">
              <WhatIfControlsPanel />
            </div>

          </main>

          {/* Bottom HUD */}
          <div className="pointer-events-none pb-6 px-4 flex flex-col md:flex-row justify-center items-center gap-4">
            <A5EmergencyControl />
            <A4StrategyControl />
          </div>
        </div>
      )}
    </div>
  );
};
