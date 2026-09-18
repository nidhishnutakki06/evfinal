import { Box, Cylinder } from '@react-three/drei'
import { SolarArray } from './SolarPanel'

export function ChargingShed({ position = [0, 0, 0], rotation = [0, 0, 0] }: any) {
  const pillarXs = [-9, -3, 3, 9]

  return (
    <group position={position} rotation={rotation}>
      {pillarXs.map((x, i) => (
        <group key={i}>
          {/* Square concrete footings */}
          <mesh position={[x, 0.15, -3]} castShadow receiveShadow>
            <boxGeometry args={[0.5, 0.3, 0.5]} />
            <meshStandardMaterial color="#2d3038" roughness={0.85} metalness={0.15} />
          </mesh>
          <mesh position={[x, 0.15, 3]} castShadow receiveShadow>
            <boxGeometry args={[0.5, 0.3, 0.5]} />
            <meshStandardMaterial color="#2d3038" roughness={0.85} metalness={0.15} />
          </mesh>

          {/* Steel pillar shafts */}
          <Cylinder args={[0.15, 0.15, 5.5]} position={[x, 2.9, -3]} castShadow receiveShadow>
            <meshStandardMaterial color="#40454f" metalness={0.72} roughness={0.25} />
          </Cylinder>
          <Cylinder args={[0.15, 0.15, 5.5]} position={[x, 2.9, 3]} castShadow receiveShadow>
            <meshStandardMaterial color="#40454f" metalness={0.72} roughness={0.25} />
          </Cylinder>

          {/* Horizontal truss beam connecting front and back pillar */}
          <mesh position={[x, 5.5, 0]} castShadow>
            <boxGeometry args={[0.15, 0.15, 6.4]} />
            <meshStandardMaterial color="#40454f" metalness={0.72} roughness={0.25} />
          </mesh>
        </group>
      ))}

      {/* Longitudinal top rails connecting pillar pairs */}
      <mesh position={[0, 5.5, -3]} castShadow>
        <boxGeometry args={[22, 0.12, 0.12]} />
        <meshStandardMaterial color="#4a5060" metalness={0.75} roughness={0.25} />
      </mesh>
      <mesh position={[0, 5.5, 3]} castShadow>
        <boxGeometry args={[22, 0.12, 0.12]} />
        <meshStandardMaterial color="#4a5060" metalness={0.75} roughness={0.25} />
      </mesh>

      {/* Roof canopy — steel-grey with subtle metallic sheen (thinner) */}
      <Box args={[22, 0.1, 8]} position={[0, 5.61, 0]} castShadow receiveShadow>
        <meshStandardMaterial color="#363b44" metalness={0.55} roughness={0.5} />
      </Box>

      {/* Fascia trim strips (front + back edge of canopy) */}
      <Box args={[22, 0.15, 0.1]} position={[0, 5.61, 4.05]} castShadow>
        <meshStandardMaterial color="#5a6070" metalness={0.7} roughness={0.3} />
      </Box>
      <Box args={[22, 0.15, 0.1]} position={[0, 5.61, -4.05]} castShadow>
        <meshStandardMaterial color="#5a6070" metalness={0.7} roughness={0.3} />
      </Box>

      {/* Solar array on top of canopy — id preserved from Phase 13 fix */}
      <SolarArray
        id="solar-shed"
        rows={2}
        cols={8}
        spacingX={2.2}
        spacingZ={3.2}
        position={[0, 5.75, 0]}
        rotation={[0, 0, 0]}
      />
    </group>
  )
}
