import { Grid, ContactShadows } from '@react-three/drei'

export function Ground() {
  return (
    <group>
      {/*
        Technical blueprint grid — darker cells for better contrast against
        the new road surfaces, brighter section lines for scale reference.
      */}
      <Grid
        position={[0, -0.01, 0]}
        args={[200, 200]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#1a1e28"
        sectionSize={10}
        sectionThickness={1.2}
        sectionColor="#2d3550"
        fadeDistance={110}
        fadeStrength={1.5}
      />

      {/* Dark asphalt-tone base plane — receives hard shadows */}
      <mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}>
        <planeGeometry args={[300, 300]} />
        <meshStandardMaterial color="#0c0e14" roughness={0.95} metalness={0.05} depthWrite={false} />
      </mesh>

      {/* Soft baked contact shadows — frames=1 since scene objects are static */}
      <ContactShadows
        position={[0, -0.01, 0]}
        opacity={0.45}
        scale={80}
        blur={2.5}
        far={12}
        frames={1}
      />
    </group>
  )
}
