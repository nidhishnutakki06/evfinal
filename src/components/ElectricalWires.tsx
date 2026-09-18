import { Interactive } from './Interactive'
import { Box } from '@react-three/drei'

export function ElectricalWires() {
  return (
    <Interactive id="wires-main" type="wire" position={[0, 0.02, 0]}>
      {/* Ground-level concrete/steel cable conduit running from Transformer to Shed */}
      <Box args={[1, 0.1, 18]} position={[-25, 0.05, -11]} receiveShadow castShadow>
         <meshStandardMaterial color="#475569" roughness={0.9} />
      </Box>
      <Box args={[26, 0.1, 1]} position={[-12.5, 0.05, -2.5]} receiveShadow castShadow>
         <meshStandardMaterial color="#475569" roughness={0.9} />
      </Box>
      <Box args={[1, 0.1, 11]} position={[0, 0.05, 2.5]} receiveShadow castShadow>
         <meshStandardMaterial color="#475569" roughness={0.9} />
      </Box>

      {/* Ground-level cable conduit to Building */}
      <Box args={[26, 0.1, 1]} position={[-12.5, 0.05, -20]} receiveShadow castShadow>
         <meshStandardMaterial color="#475569" roughness={0.9} />
      </Box>
    </Interactive>
  )
}
