import { Canvas } from '@react-three/fiber'
import { DigitalTwinScene } from './scene/DigitalTwinScene'
import { SelectionState } from './state/SelectionStore'
import './index.css'

function App() {
  return (
    <Canvas
      shadows
      camera={{ position: [25, 18, 35], fov: 45, near: 0.5, far: 300 }}
      onPointerMissed={() => SelectionState.clear()}
      dpr={[1, 1.5]}
      gl={{ antialias: true, powerPreference: 'high-performance', logarithmicDepthBuffer: true }}
    >
      <DigitalTwinScene />
    </Canvas>
  )
}

export default App
