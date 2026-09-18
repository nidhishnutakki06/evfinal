import { Box, Cylinder } from '@react-three/drei'
import { useSystemState } from '../state/MockState'
import { Interactive } from './Interactive'

// ── Generic Battery Visualization ───────────────────────────────────────────
function BatteryVisual({ soc, solar_contribution, a3_risk }: { soc?: number, solar_contribution?: number, a3_risk?: string }) {
  const fillPercentage = Math.max(0, Math.min(100, soc || 0)) / 100
  const isSolar = solar_contribution !== undefined && solar_contribution > 0
  const isA3Risk = a3_risk !== undefined && a3_risk !== 'NONE'

  // Glowing fill bar
  return (
    <group position={[0, 0.4, 0]}>
      {/* Sleek dark panel housing */}
      <Box args={[0.9, 0.08, 1.4]} receiveShadow castShadow>
        <meshStandardMaterial color="#1a1c23" metalness={0.6} roughness={0.4} />
      </Box>
      <Box args={[0.8, 0.09, 1.3]} position={[0, 0.01, 0]}>
        <meshStandardMaterial color="#000" />
      </Box>

      {/* SoC Fill Bar */}
      <Box args={[0.7, 0.1, Math.max(0.01, 1.2 * fillPercentage)]} position={[0, 0.015, -0.6 * (1 - fillPercentage)]}>
        <meshStandardMaterial color="#4ade80" emissive="#4ade80" emissiveIntensity={0.8} toneMapped={false} />
      </Box>

      {/* Solar Overlay (Additive Blue Ring) */}
      {isSolar && (
        <Box args={[0.95, 0.04, 1.45]} position={[0, -0.02, 0]}>
          <meshStandardMaterial color="#00aaff" emissive="#00aaff" emissiveIntensity={1} toneMapped={false} />
        </Box>
      )}

      {/* A3 Risk Overlay (Additive Amber Ring) */}
      {isA3Risk && (
        <Box args={[0.95, 0.04, 1.45]} position={[0, 0.04, 0]}>
          <meshStandardMaterial color="#f59e0b" emissive="#f59e0b" emissiveIntensity={1.2} toneMapped={false} />
        </Box>
      )}
    </group>
  )
}

// ── Shared Wheel Component ──────────────────────────────────────────────────
function Wheel({ position, scale = 1 }: { position: [number, number, number], scale?: number }) {
  return (
    <group position={position} scale={scale}>
      <Cylinder args={[0.35, 0.35, 0.18, 32]} rotation={[0, 0, Math.PI / 2]} castShadow receiveShadow>
        <meshStandardMaterial color="#111317" roughness={0.9} />
      </Cylinder>
      {/* Alloy rim */}
      <Cylinder args={[0.22, 0.22, 0.19, 16]} rotation={[0, 0, Math.PI / 2]}>
        <meshStandardMaterial color="#94a3b8" metalness={0.8} roughness={0.2} />
      </Cylinder>
    </group>
  )
}

// ── 1. SUV ──────────────────────────────────────────────────────────────────
export function SUV({ ev_id, position = [0, 0, 0], rotation = [0, 0, 0] }: { ev_id: string, position?: [number, number, number], rotation?: [number, number, number] }) {
  const state = useSystemState()
  const evData = state.evs?.find(e => e.ev_id === ev_id)

  return (
    <Interactive id={ev_id} type="ev" position={position} rotation={rotation}>
      <group scale={1.15}>
        {/* Main Lower Body */}
        <Box args={[1.8, 0.7, 4.4]} position={[0, 0.75, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#1e293b" metalness={0.6} roughness={0.4} />
        </Box>
        {/* Upper Cabin */}
        <Box args={[1.6, 0.65, 2.6]} position={[0, 1.42, -0.3]} castShadow receiveShadow>
          <meshStandardMaterial color="#0f172a" roughness={0.1} metalness={0.8} />
        </Box>
        {/* Hood */}
        <Box args={[1.7, 0.1, 1.0]} position={[0, 1.05, 1.6]} rotation={[0.1, 0, 0]} castShadow>
          <meshStandardMaterial color="#1e293b" metalness={0.6} roughness={0.4} />
        </Box>
        {/* Headlights & Taillights */}
        <Box args={[1.6, 0.15, 0.1]} position={[0, 0.8, 2.2]}>
           <meshStandardMaterial color="#fff" emissive="#fff" emissiveIntensity={1} toneMapped={false} />
        </Box>
        <Box args={[1.6, 0.1, 0.1]} position={[0, 0.95, -2.2]}>
           <meshStandardMaterial color="#f00" emissive="#f00" emissiveIntensity={1.5} toneMapped={false} />
        </Box>
        {/* Wheels */}
        <Wheel position={[-0.95, 0.4, 1.4]} scale={1.2} />
        <Wheel position={[0.95, 0.4, 1.4]} scale={1.2} />
        <Wheel position={[-0.95, 0.4, -1.4]} scale={1.2} />
        <Wheel position={[0.95, 0.4, -1.4]} scale={1.2} />
        
        <BatteryVisual soc={evData?.current_soc} solar_contribution={evData?.solar_contribution} a3_risk={evData?.a3_risk} />
      </group>
    </Interactive>
  )
}

// ── 2. Sedan ────────────────────────────────────────────────────────────────
export function Sedan({ ev_id, position = [0, 0, 0], rotation = [0, 0, 0] }: { ev_id: string, position?: [number, number, number], rotation?: [number, number, number] }) {
  const state = useSystemState()
  const evData = state.evs?.find(e => e.ev_id === ev_id)

  return (
    <Interactive id={ev_id} type="ev" position={position} rotation={rotation}>
      <group scale={1.15}>
        <Box args={[1.7, 0.55, 4.6]} position={[0, 0.65, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#94a3b8" metalness={0.7} roughness={0.25} />
        </Box>
        <Box args={[1.5, 0.5, 2.2]} position={[0, 1.17, -0.2]} castShadow receiveShadow>
          <meshStandardMaterial color="#0f172a" roughness={0.1} metalness={0.8} />
        </Box>
        <Box args={[1.6, 0.05, 1.0]} position={[0, 0.9, 1.7]} rotation={[0.08, 0, 0]} castShadow>
          <meshStandardMaterial color="#94a3b8" metalness={0.7} roughness={0.25} />
        </Box>
        {/* Trunk */}
        <Box args={[1.6, 0.05, 0.9]} position={[0, 0.9, -1.8]} rotation={[-0.05, 0, 0]} castShadow>
          <meshStandardMaterial color="#94a3b8" metalness={0.7} roughness={0.25} />
        </Box>
        {/* Lights */}
        <Box args={[1.5, 0.12, 0.1]} position={[0, 0.7, 2.3]}>
           <meshStandardMaterial color="#fff" emissive="#e0f2fe" emissiveIntensity={1} toneMapped={false} />
        </Box>
        <Box args={[1.5, 0.12, 0.1]} position={[0, 0.8, -2.3]}>
           <meshStandardMaterial color="#f00" emissive="#ef4444" emissiveIntensity={1.5} toneMapped={false} />
        </Box>
        {/* Wheels */}
        <Wheel position={[-0.9, 0.35, 1.5]} scale={1.05} />
        <Wheel position={[0.9, 0.35, 1.5]} scale={1.05} />
        <Wheel position={[-0.9, 0.35, -1.5]} scale={1.05} />
        <Wheel position={[0.9, 0.35, -1.5]} scale={1.05} />
        
        <BatteryVisual soc={evData?.current_soc} solar_contribution={evData?.solar_contribution} a3_risk={evData?.a3_risk} />
      </group>
    </Interactive>
  )
}

// ── 3. Hatchback ────────────────────────────────────────────────────────────
export function Hatchback({ ev_id, position = [0, 0, 0], rotation = [0, 0, 0] }: { ev_id: string, position?: [number, number, number], rotation?: [number, number, number] }) {
  const state = useSystemState()
  const evData = state.evs?.find(e => e.ev_id === ev_id)

  return (
    <Interactive id={ev_id} type="ev" position={position} rotation={rotation}>
      <group scale={1.15}>
        <Box args={[1.6, 0.6, 3.8]} position={[0, 0.65, 0.2]} castShadow receiveShadow>
          <meshStandardMaterial color="#dc2626" metalness={0.6} roughness={0.4} />
        </Box>
        <Box args={[1.4, 0.65, 2.0]} position={[0, 1.25, 0.7]} castShadow receiveShadow>
          <meshStandardMaterial color="#0f172a" roughness={0.1} metalness={0.8} />
        </Box>
        <Box args={[1.5, 0.1, 0.8]} position={[0, 0.95, 1.7]} rotation={[0.15, 0, 0]} castShadow>
          <meshStandardMaterial color="#dc2626" metalness={0.6} roughness={0.4} />
        </Box>
        {/* Flat rear back */}
        <Box args={[1.4, 0.1, 0.1]} position={[0, 0.9, -1.7]}>
           <meshStandardMaterial color="#f00" emissive="#ef4444" emissiveIntensity={1.2} toneMapped={false} />
        </Box>
        <Box args={[1.4, 0.12, 0.1]} position={[0, 0.75, 2.1]}>
           <meshStandardMaterial color="#fff" emissive="#fff" emissiveIntensity={1} toneMapped={false} />
        </Box>
        <Wheel position={[-0.85, 0.35, 1.5]} scale={1.0} />
        <Wheel position={[0.85, 0.35, 1.5]} scale={1.0} />
        <Wheel position={[-0.85, 0.35, -1.1]} scale={1.0} />
        <Wheel position={[0.85, 0.35, -1.1]} scale={1.0} />
        
        <BatteryVisual soc={evData?.current_soc} solar_contribution={evData?.solar_contribution} a3_risk={evData?.a3_risk} />
      </group>
    </Interactive>
  )
}

// ── 4. Electric Scooter (Modern Ather/Ola style) ────────────────────────────
export function Scooter({ ev_id, position = [0, 0, 0], rotation = [0, 0, 0] }: { ev_id: string, position?: [number, number, number], rotation?: [number, number, number] }) {
  const state = useSystemState()
  const evData = state.evs?.find(e => e.ev_id === ev_id)

  return (
    <Interactive id={ev_id} type="ev" position={position} rotation={rotation}>
      <group scale={1.15}>
        {/* Step-through Deck */}
        <Box args={[0.5, 0.15, 0.8]} position={[0, 0.25, 0.2]} castShadow receiveShadow>
          <meshStandardMaterial color="#334155" roughness={0.8} />
        </Box>
        {/* Front fairing & stem */}
        <Box args={[0.45, 0.9, 0.3]} position={[0, 0.7, 0.7]} rotation={[-0.2, 0, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#f8fafc" metalness={0.5} roughness={0.3} />
        </Box>
        {/* Headlight strip */}
        <Box args={[0.35, 0.05, 0.05]} position={[0, 0.9, 0.85]} rotation={[-0.2, 0, 0]}>
           <meshStandardMaterial color="#fff" emissive="#e0f2fe" emissiveIntensity={1.5} toneMapped={false} />
        </Box>
        {/* Handlebars & Dash */}
        <Box args={[0.7, 0.15, 0.2]} position={[0, 1.2, 0.6]} rotation={[-0.1, 0, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#0f172a" />
        </Box>
        {/* Under-seat Body */}
        <Box args={[0.5, 0.5, 0.9]} position={[0, 0.5, -0.4]} rotation={[0.1, 0, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#f8fafc" metalness={0.5} roughness={0.3} />
        </Box>
        {/* Seat */}
        <Box args={[0.4, 0.15, 0.8]} position={[0, 0.8, -0.45]} castShadow receiveShadow>
          <meshStandardMaterial color="#1e293b" roughness={0.9} />
        </Box>
        {/* Taillight */}
        <Box args={[0.3, 0.05, 0.05]} position={[0, 0.75, -0.85]}>
           <meshStandardMaterial color="#f00" emissive="#ef4444" emissiveIntensity={1.5} toneMapped={false} />
        </Box>
        
        {/* Scooter Wheels */}
        <group position={[0, 0.2, 0.8]}>
          <Cylinder args={[0.2, 0.2, 0.12, 32]} rotation={[0, 0, Math.PI / 2]} castShadow receiveShadow>
            <meshStandardMaterial color="#111" />
          </Cylinder>
          <Cylinder args={[0.12, 0.12, 0.13, 16]} rotation={[0, 0, Math.PI / 2]}>
            <meshStandardMaterial color="#94a3b8" metalness={0.8} />
          </Cylinder>
        </group>
        <group position={[0, 0.2, -0.7]}>
          <Cylinder args={[0.2, 0.2, 0.12, 32]} rotation={[0, 0, Math.PI / 2]} castShadow receiveShadow>
            <meshStandardMaterial color="#111" />
          </Cylinder>
          <Cylinder args={[0.12, 0.12, 0.13, 16]} rotation={[0, 0, Math.PI / 2]}>
            <meshStandardMaterial color="#94a3b8" metalness={0.8} />
          </Cylinder>
        </group>

        <group position={[0, 0.1, 0]} scale={0.5}>
          <BatteryVisual soc={evData?.current_soc} solar_contribution={evData?.solar_contribution} a3_risk={evData?.a3_risk} />
        </group>
      </group>
    </Interactive>
  )
}

// ── 5. Electric Motorcycle (Proper Street-Bike Silhouette) ──────────────────
export function Bike({ ev_id, position = [0, 0, 0], rotation = [0, 0, 0] }: { ev_id: string, position?: [number, number, number], rotation?: [number, number, number] }) {
  const state = useSystemState()
  const evData = state.evs?.find(e => e.ev_id === ev_id)

  return (
    <Interactive id={ev_id} type="ev" position={position} rotation={rotation}>
      <group scale={1.15}>
        {/* Central Motor / Battery Housing (replaces engine/tank) */}
        <Box args={[0.45, 0.6, 0.9]} position={[0, 0.55, 0.1]} castShadow receiveShadow>
          <meshStandardMaterial color="#0284c7" metalness={0.7} roughness={0.2} />
        </Box>
        {/* "Tank" fairing top */}
        <Box args={[0.5, 0.2, 0.6]} position={[0, 0.9, 0.3]} rotation={[0.1, 0, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#0284c7" metalness={0.7} roughness={0.2} />
        </Box>
        
        {/* Motorcycle Seat */}
        <Box args={[0.35, 0.15, 0.7]} position={[0, 0.85, -0.3]} rotation={[-0.1, 0, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#1e293b" roughness={0.9} />
        </Box>
        {/* Rear Tail/Subframe */}
        <Box args={[0.3, 0.2, 0.5]} position={[0, 0.75, -0.7]} rotation={[-0.2, 0, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#334155" metalness={0.6} />
        </Box>
        {/* Taillight */}
        <Box args={[0.2, 0.05, 0.05]} position={[0, 0.8, -0.95]}>
           <meshStandardMaterial color="#f00" emissive="#ef4444" emissiveIntensity={1.5} toneMapped={false} />
        </Box>

        {/* Front Forks & Headlight */}
        <Cylinder args={[0.04, 0.04, 0.8]} position={[-0.15, 0.6, 0.9]} rotation={[-0.3, 0, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#cbd5e1" metalness={0.9} roughness={0.1} />
        </Cylinder>
        <Cylinder args={[0.04, 0.04, 0.8]} position={[0.15, 0.6, 0.9]} rotation={[-0.3, 0, 0]} castShadow receiveShadow>
          <meshStandardMaterial color="#cbd5e1" metalness={0.9} roughness={0.1} />
        </Cylinder>
        <Box args={[0.3, 0.2, 0.15]} position={[0, 0.9, 0.85]} rotation={[-0.3, 0, 0]}>
           <meshStandardMaterial color="#fff" emissive="#e0f2fe" emissiveIntensity={1.5} toneMapped={false} />
        </Box>
        {/* Handlebars */}
        <Cylinder args={[0.02, 0.02, 0.7]} position={[0, 1.05, 0.7]} rotation={[0, 0, Math.PI / 2]} castShadow receiveShadow>
          <meshStandardMaterial color="#111" />
        </Cylinder>

        {/* Motorcycle Wheels (Thicker/larger than scooter) */}
        <group position={[0, 0.35, 1.0]}>
          <Cylinder args={[0.35, 0.35, 0.15, 32]} rotation={[0, 0, Math.PI / 2]} castShadow receiveShadow>
            <meshStandardMaterial color="#111" />
          </Cylinder>
          {/* Rims */}
          <Cylinder args={[0.22, 0.22, 0.16, 16]} rotation={[0, 0, Math.PI / 2]}>
            <meshStandardMaterial color="#334155" metalness={0.8} />
          </Cylinder>
        </group>
        <group position={[0, 0.35, -0.8]}>
          <Cylinder args={[0.35, 0.35, 0.18, 32]} rotation={[0, 0, Math.PI / 2]} castShadow receiveShadow>
            <meshStandardMaterial color="#111" />
          </Cylinder>
          {/* Rims */}
          <Cylinder args={[0.22, 0.22, 0.19, 16]} rotation={[0, 0, Math.PI / 2]}>
            <meshStandardMaterial color="#334155" metalness={0.8} />
          </Cylinder>
        </group>

        <group position={[0, 0.15, 0.1]} scale={0.5}>
          <BatteryVisual soc={evData?.current_soc} solar_contribution={evData?.solar_contribution} a3_risk={evData?.a3_risk} />
        </group>
      </group>
    </Interactive>
  )
}
