import { useSystemState } from '../state/MockState'
import { Environment as DreiEnvironment, Sky, Cloud } from '@react-three/drei'
import { useFrame } from '@react-three/fiber'
import { useRef, useMemo } from 'react'
import * as THREE from 'three'

// ── Rain ────────────────────────────────────────────────────────────────────
// Rendered as instanced thin boxes (streak effect) so rain is clearly visible.
// InstancedMesh mutates only instanceMatrix each frame — no Float32Array realloc.
const RAIN_COUNT = 900

function Rain() {
  const meshRef = useRef<THREE.InstancedMesh>(null)
  const dummy = useMemo(() => new THREE.Object3D(), [])

  // Stable per-particle positions — Float32Array mutated in-place every frame
  const positions = useMemo(() => {
    const arr = new Float32Array(RAIN_COUNT * 3)
    for (let i = 0; i < RAIN_COUNT; i++) {
      arr[i * 3]     = (Math.random() - 0.5) * 160
      arr[i * 3 + 1] = Math.random() * 60
      arr[i * 3 + 2] = (Math.random() - 0.5) * 160
    }
    return arr
  }, [])

  useFrame((_, delta) => {
    if (!meshRef.current) return
    for (let i = 0; i < RAIN_COUNT; i++) {
      positions[i * 3 + 1] -= delta * 30
      if (positions[i * 3 + 1] < 0) positions[i * 3 + 1] = 60
      dummy.position.set(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2])
      dummy.updateMatrix()
      meshRef.current.setMatrixAt(i, dummy.matrix)
    }
    meshRef.current.instanceMatrix.needsUpdate = true
  })

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, RAIN_COUNT]}>
      {/* Thin vertical box — visually reads as a falling raindrop streak */}
      <boxGeometry args={[0.04, 0.55, 0.04]} />
      <meshBasicMaterial color="#99bbdd" transparent opacity={0.78} />
    </instancedMesh>
  )
}

// ── WeatherEnvironment ───────────────────────────────────────────────────────
// Reads ONLY from SystemState.environment.weather and .time_of_day.
// Does NOT compute or alter any energy/EV/solar/building values.
export function WeatherEnvironment() {
  const state = useSystemState()

  // Exact backend fields — not modified, only read
  const weatherStr = state.environment?.weather   || 'Sunny'
  const timeStr    = state.environment?.time_of_day || 'Morning'

  const isNight  = timeStr    === 'Night'   || timeStr    === 'Evening'
  const isRain   = weatherStr === 'Rain'    || weatherStr === 'Rainy'
  const isCloudy = weatherStr === 'Cloudy'  || isRain

  // ── Per-state configuration ───────────────────────────────────────────────
  // Lighting: warm golden for Sunny, cool grey for Cloudy/Rain, deep blue for Night
  const ambientColor      = isNight ? '#06090f' : isCloudy ? '#7080a0' : '#fff2d8'
  const ambientIntensity  = isNight ? 0.06      : isCloudy ? 0.18      : 0.4
  const dirLightColor     = isNight ? '#1a2040' : isCloudy ? '#8090a8' : '#fff5d0'
  const dirLightIntensity = isNight ? 0.04      : isCloudy ? 0.35      : 1.5
  const sunPos: [number, number, number] = isNight ? [30, -10, 20] : [50, 65, 20]

  // Hemisphere sky/ground bounce
  const hemiSky       = isNight ? '#040815'  : isCloudy ? '#5a6880' : '#87ceeb'
  const hemiGround    = isNight ? '#050a06'  : '#222a18'
  const hemiIntensity = isNight ? 0.1        : isCloudy ? 0.28      : 0.55

  // Background colour and fog — chosen to match sky so the horizon blends cleanly
  const bgColor = isNight ? '#020408' : isRain ? '#3a4252' : isCloudy ? '#555f6e' : '#5da8e0'
  const fogNear = isRain ? 35  : isCloudy ? 55  : isNight ? 50  : 90
  const fogFar  = isRain ? 110 : isCloudy ? 170 : isNight ? 140 : 240

  const envPreset = isNight ? 'night' : isCloudy ? 'warehouse' : 'city'

  // Sky turbidity/scattering — dramatically different per weather state
  const turbidity        = isRain ? 14 : isCloudy ? 9 : 1.5
  const rayleigh         = isRain ? 4  : isCloudy ? 3 : 0.8
  const mieCoefficient   = isCloudy ? 0.06 : 0.005

  return (
    <>
      {/* Scene-level colour and fog — placed outside group so they attach to the scene */}
      <color attach="background" args={[bgColor]} />
      {/* Fog: tight near/far for Rain makes weather change dramatically obvious */}
      <fog attach="fog" args={[bgColor, fogNear, fogFar]} />

      {/* Ambient + hemisphere bounce */}
      <ambientLight intensity={ambientIntensity} color={ambientColor} />
      <hemisphereLight color={hemiSky} groundColor={hemiGround} intensity={hemiIntensity} />

      {/* Primary directional / sun light — wider frustum covers roads + landscaping */}
      <directionalLight
        castShadow
        position={sunPos}
        intensity={dirLightIntensity}
        color={dirLightColor}
        shadow-mapSize-width={1024}
        shadow-mapSize-height={1024}
        shadow-camera-near={0.5}
        shadow-camera-far={130}
        shadow-camera-left={-55}
        shadow-camera-right={55}
        shadow-camera-top={50}
        shadow-camera-bottom={-50}
        shadow-bias={-0.001}
      />

      {/* HDRI environment map — affects material reflections */}
      <DreiEnvironment preset={envPreset as any} />

      {/* Sky dome (daytime only) — turbidity/rayleigh tuned per weather state */}
      {!isNight && (
        <Sky
          sunPosition={sunPos}
          turbidity={turbidity}
          rayleigh={rayleigh}
          mieCoefficient={mieCoefficient}
          mieDirectionalG={0.75}
        />
      )}

      {/* Cloud layers — three groups at staggered heights for depth */}
      {isCloudy && (
        <>
          <group position={[0, 38, -5]}>
            <Cloud
              opacity={isRain ? 0.75 : 0.5}
              speed={isRain ? 0.4 : 0.2}
              bounds={[65, 14, 65]}
              segments={12}
            />
          </group>
          <group position={[25, 42, 20]}>
            <Cloud
              opacity={isRain ? 0.6 : 0.35}
              speed={0.2}
              bounds={[45, 10, 45]}
              segments={8}
            />
          </group>
          <group position={[-20, 40, -20]}>
            <Cloud
              opacity={isRain ? 0.5 : 0.3}
              speed={0.15}
              bounds={[40, 8, 40]}
              segments={8}
            />
          </group>
        </>
      )}

      {/* Streak rain — clearly visible falling boxes (instanced for performance) */}
      {isRain && <Rain />}
    </>
  )
}
