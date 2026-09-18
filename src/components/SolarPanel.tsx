import { Interactive } from './Interactive'

// ── SolarPanel ───────────────────────────────────────────────────────────────
// Improved visual: angled aluminium bracket legs, proper panel frame,
// high-metalness PV cell surface, horizontal + vertical cell divider strips.
export function SolarPanel({ position = [0, 0, 0], rotation = [0, 0, 0], scale = 1 }: any) {
  return (
    <group position={position} rotation={rotation} scale={scale}>
      {/* Mounting bracket legs (front pair taller, back pair shorter for tilt) */}
      <mesh position={[-0.6, 0.27, 0.8]} castShadow>
        <boxGeometry args={[0.08, 0.54, 0.08]} />
        <meshStandardMaterial color="#3d4350" metalness={0.75} roughness={0.35} />
      </mesh>
      <mesh position={[0.6, 0.27, 0.8]} castShadow>
        <boxGeometry args={[0.08, 0.54, 0.08]} />
        <meshStandardMaterial color="#3d4350" metalness={0.75} roughness={0.35} />
      </mesh>
      <mesh position={[-0.6, 0.18, -0.8]} castShadow>
        <boxGeometry args={[0.08, 0.36, 0.08]} />
        <meshStandardMaterial color="#3d4350" metalness={0.75} roughness={0.35} />
      </mesh>
      <mesh position={[0.6, 0.18, -0.8]} castShadow>
        <boxGeometry args={[0.08, 0.36, 0.08]} />
        <meshStandardMaterial color="#3d4350" metalness={0.75} roughness={0.35} />
      </mesh>

      {/* Horizontal cross-rail */}
      <mesh position={[0, 0.46, 0]} castShadow>
        <boxGeometry args={[1.4, 0.06, 0.06]} />
        <meshStandardMaterial color="#4a5060" metalness={0.8} roughness={0.3} />
      </mesh>

      {/* Panel assembly — tilted like a real solar panel (-0.28 rad ≈ 16°) */}
      <group position={[0, 0.68, 0]} rotation={[-0.28, 0, 0]}>
        {/* Aluminium frame */}
        <mesh castShadow>
          <boxGeometry args={[2.1, 0.06, 3.1]} />
          <meshStandardMaterial color="#687080" metalness={0.8} roughness={0.25} />
        </mesh>

        {/* PV cell glass surface — high metalness, very low roughness */}
        <mesh position={[0, 0.04, 0]}>
          <boxGeometry args={[1.9, 0.04, 2.9]} />
          <meshStandardMaterial color="#0f172a" metalness={0.95} roughness={0.05} />
        </mesh>

        {/* Horizontal cell dividers (creates 3 rows of cells) */}
        {([-0.75, 0.75] as const).map((z, i) => (
          <mesh key={`h${i}`} position={[0, 0.065, z]}>
            <boxGeometry args={[1.88, 0.02, 0.025]} />
            <meshBasicMaterial color="#334155" />
          </mesh>
        ))}

        {/* Vertical cell dividers (creates 4 columns of cells) */}
        {([-0.47, 0, 0.47] as const).map((x, i) => (
          <mesh key={`v${i}`} position={[x, 0.065, 0]}>
            <boxGeometry args={[0.025, 0.02, 2.88]} />
            <meshBasicMaterial color="#334155" />
          </mesh>
        ))}
      </group>
    </group>
  )
}

// ── SolarArray ───────────────────────────────────────────────────────────────
// Accepts an explicit `id` prop — ensures each array instance has a stable,
// distinct interaction ID (solar-building vs solar-shed).
export function SolarArray({
  id,
  rows = 2,
  cols = 4,
  spacingX = 2.5,
  spacingZ = 3.5,
  position = [0, 0, 0],
  rotation = [0, 0, 0],
}: any) {
  const panels = []
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      panels.push(
        <SolarPanel
          key={`${r}-${c}`}
          position={[(c - cols / 2 + 0.5) * spacingX, 0, (r - rows / 2 + 0.5) * spacingZ]}
        />,
      )
    }
  }
  return (
    <Interactive id={id} type="solar" position={position} rotation={rotation}>
      {panels}
    </Interactive>
  )
}
