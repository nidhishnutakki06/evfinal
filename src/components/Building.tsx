import { Box, Cylinder } from '@react-three/drei'
import { Interactive } from './Interactive'
import { useSystemState } from '../state/MockState'

// Normalize a kW demand value to [0, 1].
function norm(value: number, kWCeiling: number): number {
  return Math.min(1, Math.max(0, value) / kWCeiling)
}

function demandColor(n: number): string {
  if (n < 0.3) return '#22c55e'
  if (n < 0.7) return '#f59e0b'
  return '#ef4444'
}

export function Building({ position = [0, 0, 0] }: { position?: [number, number, number] }) {
  const state = useSystemState()
  const b = state.building

  // EXACT BACKEND FIELDS
  const acDemand          = b?.ac_demand          ?? 0
  const lightsDemand      = b?.lights_demand      ?? 0
  const liftsDemand       = b?.lifts_demand       ?? 0
  const appliancesDemand  = b?.appliances_demand  ?? 0
  const totalDemand       = b?.total_building_demand ?? 0

  // NORMALISATION
  const acNorm         = norm(acDemand,         20)
  const lightsNorm     = norm(lightsDemand,     10)
  const liftsNorm      = norm(liftsDemand,       5)
  const appliancesNorm = norm(appliancesDemand, 10)
  const totalNorm      = norm(totalDemand,      50)

  // Window glow intensity driven by lights_demand
  const windowEmissive  = 0.1 + lightsNorm * 1.4
  const windowColor     = lightsNorm > 0 ? '#fffbe6' : '#88ccff'

  // Window Grid Generation (Front and Back)
  const frontWindows = []
  const backWindows = []
  const cols = 8
  const rows = 4
  const wWidth = 3.2
  const wHeight = 3.6
  const spacingX = 3.4
  const spacingY = 4.0
  
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const px = (c - cols / 2 + 0.5) * spacingX
      const py = (r - rows / 2 + 0.5) * spacingY + 10 // center at y=10
      
      // Front windows
      frontWindows.push(
        <Box key={`fw-${r}-${c}`} args={[wWidth, wHeight, 0.4]} position={[px, py, 10.1]} castShadow>
          <meshPhysicalMaterial
            color={windowColor}
            emissive={lightsNorm > 0 ? '#fffbe6' : '#000000'}
            emissiveIntensity={windowEmissive}
            transmission={0.8}
            opacity={1}
            metalness={0.8}
            roughness={0.1}
            ior={1.5}
            thickness={1}
          />
        </Box>
      )
      
      // Back windows
      backWindows.push(
        <Box key={`bw-${r}-${c}`} args={[wWidth, wHeight, 0.4]} position={[px, py, -10.1]} castShadow>
          <meshPhysicalMaterial
            color={windowColor}
            emissive={lightsNorm > 0 ? '#fffbe6' : '#000000'}
            emissiveIntensity={windowEmissive * 0.6}
            transmission={0.8}
            opacity={1}
            metalness={0.8}
            roughness={0.1}
          />
        </Box>
      )
    }
  }

  return (
    <Interactive id="building-main" type="building" position={position}>
      {/* ── CORE STRUCTURE ── */}
      <Box args={[29, 19.8, 19.8]} position={[0, 9.9, 0]} receiveShadow castShadow>
        <meshStandardMaterial color="#2d3748" roughness={0.8} />
      </Box>

      {/* Vertical architectural mullions/columns */}
      {[...Array(cols + 1)].map((_, i) => (
        <Box key={`col-f-${i}`} args={[0.4, 20, 0.6]} position={[-13.6 + i * spacingX, 10, 10.1]} castShadow receiveShadow>
          <meshStandardMaterial color="#cbd5e1" roughness={0.4} metalness={0.3} />
        </Box>
      ))}
      {[...Array(cols + 1)].map((_, i) => (
        <Box key={`col-b-${i}`} args={[0.4, 20, 0.6]} position={[-13.6 + i * spacingX, 10, -10.1]} castShadow receiveShadow>
          <meshStandardMaterial color="#cbd5e1" roughness={0.4} metalness={0.3} />
        </Box>
      ))}

      {/* Horizontal spandrel beams */}
      {[...Array(rows + 1)].map((_, i) => (
        <Box key={`beam-f-${i}`} args={[28, 0.6, 0.6]} position={[0, 2 + i * spacingY, 10.1]} castShadow receiveShadow>
          <meshStandardMaterial color="#cbd5e1" roughness={0.4} metalness={0.3} />
        </Box>
      ))}
      {[...Array(rows + 1)].map((_, i) => (
        <Box key={`beam-b-${i}`} args={[28, 0.6, 0.6]} position={[0, 2 + i * spacingY, -10.1]} castShadow receiveShadow>
          <meshStandardMaterial color="#cbd5e1" roughness={0.4} metalness={0.3} />
        </Box>
      ))}

      {/* Solid side walls — shifted to avoid Z-fighting with core */}
      <Box args={[0.2, 20, 20]} position={[14.6, 10, 0]} receiveShadow castShadow>
        <meshStandardMaterial color="#f8fafc" roughness={0.9} />
      </Box>
      <Box args={[0.2, 20, 20]} position={[-14.6, 10, 0]} receiveShadow castShadow>
        <meshStandardMaterial color="#f8fafc" roughness={0.9} />
      </Box>

      {/* Glass Facade Grids */}
      {frontWindows}
      {backWindows}

      {/* ── ENTRANCE LOBBY ── */}
      <group position={[0, 0, 10.2]}>
        {/* Lobby interior box */}
        <Box args={[8, 3.8, 1.2]} position={[0, 1.9, 0.3]} receiveShadow>
          <meshStandardMaterial color="#111317" />
        </Box>
        {/* Glowing glass doors / lobby interior */}
        <Box args={[7.6, 3.6, 1.3]} position={[0, 1.8, 0.3]} castShadow receiveShadow>
          <meshPhysicalMaterial
            color={appliancesNorm > 0 ? '#fff8e1' : '#00e5ff'}
            emissive={appliancesNorm > 0 ? '#fff8e1' : '#00e5ff'}
            emissiveIntensity={appliancesNorm > 0 ? 0.3 + appliancesNorm * 1.5 : 0.6}
            transmission={0.6}
            transparent
            opacity={0.9}
            toneMapped={false}
          />
        </Box>
        {/* Entrance Awning / Canopy */}
        <Box args={[9, 0.4, 3]} position={[0, 4, 1.2]} castShadow receiveShadow>
          <meshStandardMaterial color="#cbd5e1" roughness={0.5} metalness={0.3} />
        </Box>
        {/* Awning support pillars */}
        <Cylinder args={[0.1, 0.1, 4]} position={[-4, 2, 2.5]} castShadow receiveShadow>
          <meshStandardMaterial color="#94a3b8" metalness={0.8} />
        </Cylinder>
        <Cylinder args={[0.1, 0.1, 4]} position={[4, 2, 2.5]} castShadow receiveShadow>
          <meshStandardMaterial color="#94a3b8" metalness={0.8} />
        </Cylinder>
      </group>

      {/* ── HVAC UNITS ON ROOFTOP ── */}
      {[-8, 0, 8].map((x, i) => (
        <group key={`hvac-${i}`} position={[x, 20.8, -2]}>
          {/* Main detailed casing */}
          <Box args={[3.2, 1.6, 2.4]} castShadow receiveShadow>
            <meshStandardMaterial color="#475569" metalness={0.5} roughness={0.5} />
          </Box>
          {/* Side venting grille */}
          <Box args={[3.3, 1.2, 2.2]} position={[0, 0, 0]}>
            <meshStandardMaterial color="#334155" metalness={0.3} roughness={0.8} />
          </Box>
          {/* Status indicator — glows with ac_demand intensity */}
          <Box args={[2.8, 0.15, 0.1]} position={[0, 0.5, 1.21]}>
            <meshStandardMaterial
              color={demandColor(acNorm)}
              emissive={demandColor(acNorm)}
              emissiveIntensity={0.5 + acNorm * 1.5}
              toneMapped={false}
            />
          </Box>
          {/* Dual Fan discs on top */}
          <Cylinder args={[0.6, 0.6, 0.1, 16]} position={[-0.8, 0.85, 0]} castShadow>
            <meshStandardMaterial color="#1e293b" metalness={0.8} />
          </Cylinder>
          <Cylinder args={[0.6, 0.6, 0.1, 16]} position={[0.8, 0.85, 0]} castShadow>
            <meshStandardMaterial color="#1e293b" metalness={0.8} />
          </Cylinder>
        </group>
      ))}

      {/* ── LIFT SHAFT INDICATOR ── */}
      <group position={[14.6, 0, 5]}>
        {/* Extended architectural housing for lift */}
        <Box args={[1.2, 21, 2.4]} position={[0, 10.5, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#cbd5e1" roughness={0.4} metalness={0.2} />
        </Box>
        {/* Static dark shaft track recessed inside */}
        <Box args={[0.3, 19, 0.4]} position={[0.5, 10, 0]}>
          <meshStandardMaterial color="#1e293b" />
        </Box>
        {/* Glowing moving lift cab (height scales with demand) */}
        <Box args={[0.5, 19 * liftsNorm, 0.6]} position={[0.45, 0.5 + 9.5 * liftsNorm, 0]}>
          <meshStandardMaterial
            color={demandColor(liftsNorm)}
            emissive={demandColor(liftsNorm)}
            emissiveIntensity={liftsNorm > 0 ? 0.8 + liftsNorm * 1.0 : 0}
            toneMapped={false}
          />
        </Box>
      </group>

      {/* ── TOTAL LOAD BAR ON PARAPET ── */}
      {/* Horizontal bar along the front top edge */}
      <Box args={[28 * totalNorm, 0.5, 0.4]} position={[-14 + 14 * totalNorm, 20.25, 10.3]}>
        <meshStandardMaterial
          color={demandColor(totalNorm)}
          emissive={demandColor(totalNorm)}
          emissiveIntensity={0.6 + totalNorm * 1.0}
          toneMapped={false}
        />
      </Box>

      {/* ── ROOFTOP PARAPET WALLS ── */}
      <Box args={[29.2, 1.2, 0.4]} position={[0, 20.6, 10.3]} receiveShadow castShadow>
        <meshStandardMaterial color="#94a3b8" />
      </Box>
      <Box args={[29.2, 1.2, 0.4]} position={[0, 20.6, -10.3]} receiveShadow castShadow>
        <meshStandardMaterial color="#94a3b8" />
      </Box>
      <Box args={[0.4, 1.2, 21]} position={[14.4, 20.6, 0]} receiveShadow castShadow>
        <meshStandardMaterial color="#94a3b8" />
      </Box>
      <Box args={[0.4, 1.2, 21]} position={[-14.4, 20.6, 0]} receiveShadow castShadow>
        <meshStandardMaterial color="#94a3b8" />
      </Box>
    </Interactive>
  )
}
