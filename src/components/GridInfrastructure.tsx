import { Box, Cylinder } from '@react-three/drei'
import { Interactive } from './Interactive'
import { useSystemState } from '../state/MockState'

export function GridInfrastructure({ position = [0, 0, 0], rotation = [0, 0, 0] }: any) {
  const state = useSystemState()
  const isEmergency = state.emergency?.emergency_active_state === true

  // Support & Fencing — Chainlink/metal palisade perimeter
  const fencePosts = []
  const fenceRails = []
  
  // Perimeter dimensions: x: -4.5 to 4.5, z: -3 to 3
  const xs = [-4.5, -2.25, 0, 2.25, 4.5]

  for (let x of xs) {
    fencePosts.push(<Cylinder key={`post-front-${x}`} args={[0.05, 0.05, 2.2]} position={[x, 1.1, 3]} castShadow receiveShadow><meshStandardMaterial color="#555" /></Cylinder>)
    fencePosts.push(<Cylinder key={`post-back-${x}`} args={[0.05, 0.05, 2.2]} position={[x, 1.1, -3]} castShadow receiveShadow><meshStandardMaterial color="#555" /></Cylinder>)
  }
  for (let z of [-1.5, 0, 1.5]) {
    fencePosts.push(<Cylinder key={`post-left-${z}`} args={[0.05, 0.05, 2.2]} position={[-4.5, 1.1, z]} castShadow receiveShadow><meshStandardMaterial color="#555" /></Cylinder>)
    fencePosts.push(<Cylinder key={`post-right-${z}`} args={[0.05, 0.05, 2.2]} position={[4.5, 1.1, z]} castShadow receiveShadow><meshStandardMaterial color="#555" /></Cylinder>)
  }

  // Horizontal rails
  fenceRails.push(<Box key="rail-front-top" args={[9, 0.05, 0.05]} position={[0, 2, 3]}><meshStandardMaterial color="#555" /></Box>)
  fenceRails.push(<Box key="rail-front-bot" args={[9, 0.05, 0.05]} position={[0, 0.5, 3]}><meshStandardMaterial color="#555" /></Box>)
  fenceRails.push(<Box key="rail-back-top" args={[9, 0.05, 0.05]} position={[0, 2, -3]}><meshStandardMaterial color="#555" /></Box>)
  fenceRails.push(<Box key="rail-back-bot" args={[9, 0.05, 0.05]} position={[0, 0.5, -3]}><meshStandardMaterial color="#555" /></Box>)
  fenceRails.push(<Box key="rail-left-top" args={[0.05, 0.05, 6]} position={[-4.5, 2, 0]}><meshStandardMaterial color="#555" /></Box>)
  fenceRails.push(<Box key="rail-left-bot" args={[0.05, 0.05, 6]} position={[-4.5, 0.5, 0]}><meshStandardMaterial color="#555" /></Box>)
  fenceRails.push(<Box key="rail-right-top" args={[0.05, 0.05, 6]} position={[4.5, 2, 0]}><meshStandardMaterial color="#555" /></Box>)
  fenceRails.push(<Box key="rail-right-bot" args={[0.05, 0.05, 6]} position={[4.5, 0.5, 0]}><meshStandardMaterial color="#555" /></Box>)

  // Fence mesh (simplified as transparent plane)
  const fencePlanes = (
    <>
      <mesh position={[0, 1.1, 3]} receiveShadow>
        <planeGeometry args={[9, 2.2]} />
        <meshBasicMaterial color="#333" wireframe opacity={0.3} transparent />
      </mesh>
      <mesh position={[0, 1.1, -3]} receiveShadow>
        <planeGeometry args={[9, 2.2]} />
        <meshBasicMaterial color="#333" wireframe opacity={0.3} transparent />
      </mesh>
      <mesh position={[-4.5, 1.1, 0]} rotation={[0, Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[6, 2.2]} />
        <meshBasicMaterial color="#333" wireframe opacity={0.3} transparent />
      </mesh>
      <mesh position={[4.5, 1.1, 0]} rotation={[0, Math.PI / 2, 0]} receiveShadow>
        <planeGeometry args={[6, 2.2]} />
        <meshBasicMaterial color="#333" wireframe opacity={0.3} transparent />
      </mesh>
    </>
  )

  return (
    <Interactive id="grid-main" type="grid" position={position} rotation={rotation}>
      <group scale={1.2}>
      {/* Concrete Base Pad with wider footprint */}
      <Box args={[10, 0.2, 7]} position={[0, 0.1, 0]} receiveShadow>
        <meshStandardMaterial color="#3c3f45" roughness={0.9} />
      </Box>

      {/* Perimeter Fencing */}
      <group>
        {fencePosts}
        {fenceRails}
        {fencePlanes}
      </group>

      {/* Main Transformer Unit - Substation size */}
      <Box args={[4, 3.5, 2.5]} position={[-1, 1.95, 0]} castShadow receiveShadow>
        <meshStandardMaterial color="#4a5568" roughness={0.7} metalness={0.4} />
      </Box>

      {/* Secondary control cabinet */}
      <Box args={[1.5, 2.5, 1.5]} position={[2.2, 1.45, 0]} castShadow receiveShadow>
        <meshStandardMaterial color="#cbd5e1" roughness={0.5} metalness={0.2} />
      </Box>

      {/* Warning light and label on control cabinet */}
      <Box args={[0.8, 0.5, 0.05]} position={[2.2, 2.2, 0.76]}>
        <meshStandardMaterial 
          color={isEmergency ? "#ff0000" : "#22c55e"} 
          emissive={isEmergency ? "#ff0000" : "#000000"} 
          emissiveIntensity={isEmergency ? 1.5 : 0}
          toneMapped={false}
        />
      </Box>
      <Box args={[0.6, 0.3, 0.02]} position={[2.2, 1.7, 0.76]}>
         <meshStandardMaterial color="#eab308" />
      </Box>

      {/* Cooling Radiator Banks (left and right sides of transformer) */}
      {[-0.8, -0.4, 0, 0.4, 0.8].map((z, i) => (
        <group key={`rad-${i}`}>
           {/* Left side radiators */}
           <Box args={[0.6, 2.8, 0.05]} position={[-3.2, 1.95, z]} castShadow>
             <meshStandardMaterial color="#4a5568" roughness={0.8} />
           </Box>
           <Cylinder args={[0.05, 0.05, 0.6]} position={[-3, 3, z]} rotation={[0, 0, Math.PI / 2]} castShadow>
             <meshStandardMaterial color="#4a5568" />
           </Cylinder>
           <Cylinder args={[0.05, 0.05, 0.6]} position={[-3, 1, z]} rotation={[0, 0, Math.PI / 2]} castShadow>
             <meshStandardMaterial color="#4a5568" />
           </Cylinder>
        </group>
      ))}

      {/* High-Voltage Ceramic Bushings on top */}
      {[-0.5, 0.5].map((z, i) => (
        <group key={`bushing-${i}`} position={[-1, 3.7, z]}>
          <Cylinder args={[0.2, 0.3, 0.5]} position={[0, 0.25, 0]} castShadow>
             <meshStandardMaterial color="#94a3b8" roughness={0.3} />
          </Cylinder>
          {[0, 0.1, 0.2, 0.3].map((y) => (
            <Cylinder key={`ring-${y}`} args={[0.3, 0.3, 0.05]} position={[0, y + 0.1, 0]} castShadow>
              <meshStandardMaterial color="#94a3b8" roughness={0.3} />
            </Cylinder>
          ))}
          <Cylinder args={[0.05, 0.05, 0.8]} position={[0, 0.65, 0]} castShadow>
             <meshStandardMaterial color="#9ca3af" metalness={0.8} roughness={0.2} />
          </Cylinder>
        </group>
      ))}

      {/* Conduits between Transformer and Control Cabinet */}
      <Cylinder args={[0.1, 0.1, 1.5]} position={[1.2, 1.5, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
        <meshStandardMaterial color="#64748b" metalness={0.6} />
      </Cylinder>
      <Cylinder args={[0.1, 0.1, 1.5]} position={[1.2, 1.0, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
        <meshStandardMaterial color="#64748b" metalness={0.6} />
      </Cylinder>
      </group>
    </Interactive>
  )
}
