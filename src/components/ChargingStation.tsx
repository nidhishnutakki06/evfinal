import { Box, RoundedBox, Cylinder } from '@react-three/drei'
import { Interactive } from './Interactive'
import { useSystemState } from '../state/MockState'
import * as THREE from 'three'
import { useMemo } from 'react'

export function ChargingStation({ station_id, position = [0, 0, 0], rotation = [0, 0, 0] }: any) {
  const state = useSystemState()
  const stationData = state.stations?.find(s => s.station_id === station_id)
  const evData = state.evs?.find(e => e.ev_id === stationData?.connected_ev_id)

  let ledColor = "#00e5ff" // Cyan = no EV connected
  if (evData) {
    const currentRate = evData.current_rate ?? 0
    const maxRate = evData.maximum_rate ?? 0

    if (currentRate === 0) {
      ledColor = "#ff0000"
    } else if (currentRate < maxRate) {
      ledColor = "#ffff00"
    } else {
      ledColor = "#00ff00"
    }
  }

  // Cable Curve Definition
  // If an EV is connected, curve to the EV position (Z offset +2.5 based on scene layout).
  // Otherwise, create a short loop returning to the holster on the side of the charger.
  const cableCurve = useMemo(() => {
    if (evData) {
      return new THREE.QuadraticBezierCurve3(
        new THREE.Vector3(0.28, 1.3, 0.0),  // start at charger side
        new THREE.Vector3(0.8, 0.1, 1.2),   // droop to ground
        new THREE.Vector3(0.4, 0.5, 2.2)    // end at EV charge port (approximate side of EV)
      )
    } else {
      return new THREE.QuadraticBezierCurve3(
        new THREE.Vector3(0.28, 1.3, 0.0),  // start at charger side
        new THREE.Vector3(0.4, 0.6, 0.2),   // small droop loop
        new THREE.Vector3(0.28, 0.9, 0.1)   // end at holster
      )
    }
  }, [evData])

  return (
    <Interactive id={station_id || 'unknown-station'} type="station" position={position} rotation={rotation}>
      {/* Base Footing */}
      <Box args={[0.7, 0.1, 0.5]} position={[0, 0.05, 0]} castShadow receiveShadow>
        <meshStandardMaterial color="#1a1c20" roughness={0.9} />
      </Box>
      
      {/* Main Pedestal Body - Sleek angled front */}
      <mesh position={[0, 1.05, -0.05]} castShadow receiveShadow>
         {/* Simple box for now, slightly taller and wider */}
         <boxGeometry args={[0.5, 2.0, 0.3]} />
         <meshStandardMaterial color="#e2e8f0" roughness={0.3} metalness={0.2} />
      </mesh>

      {/* Front dark glass panel for display */}
      <RoundedBox args={[0.4, 1.6, 0.05]} position={[0, 1.2, 0.12]} radius={0.02} castShadow>
        <meshStandardMaterial color="#0f172a" roughness={0.1} metalness={0.8} />
      </RoundedBox>

      {/* Screen Interface */}
      <Box args={[0.3, 0.4, 0.02]} position={[0, 1.5, 0.15]}>
        <meshStandardMaterial color="#000" emissive="#0ea5e9" emissiveIntensity={0.2} />
      </Box>
      
      {/* Small UI detail on screen */}
      <Box args={[0.2, 0.05, 0.01]} position={[0, 1.55, 0.16]}>
        <meshBasicMaterial color="#ffffff" />
      </Box>

      {/* Status LED Indicator Strip (replaces simple ring) */}
      <Box args={[0.4, 0.04, 0.02]} position={[0, 1.9, 0.15]}>
        <meshStandardMaterial color={ledColor} emissive={ledColor} emissiveIntensity={1.2} toneMapped={false} />
      </Box>
      <Box args={[0.4, 0.04, 0.02]} position={[0, 0.5, 0.15]}>
        <meshStandardMaterial color={ledColor} emissive={ledColor} emissiveIntensity={0.5} toneMapped={false} />
      </Box>

      {/* Cable Holster (Right side) */}
      <Box args={[0.1, 0.2, 0.15]} position={[0.28, 0.9, 0.1]} castShadow>
         <meshStandardMaterial color="#334155" roughness={0.6} />
      </Box>

      {/* Cable Outlet (Right side higher up) */}
      <Cylinder args={[0.04, 0.04, 0.1]} position={[0.25, 1.3, 0]} rotation={[0, 0, Math.PI / 2]} castShadow>
         <meshStandardMaterial color="#1e293b" />
      </Cylinder>

      {/* Dynamic Cable */}
      <mesh castShadow>
         <tubeGeometry args={[cableCurve, 20, 0.025, 8, false]} />
         <meshStandardMaterial color="#0f172a" roughness={0.8} />
      </mesh>

      {/* Connector Plug (at the end of the cable) */}
      <group position={cableCurve.getPoint(1)}>
         <mesh rotation={[Math.PI / 4, 0, 0]} castShadow>
           <boxGeometry args={[0.08, 0.15, 0.08]} />
           <meshStandardMaterial color="#cbd5e1" metalness={0.6} roughness={0.3} />
         </mesh>
         <mesh position={[0, 0.1, 0]} rotation={[Math.PI / 4, 0, 0]} castShadow>
           <cylinderGeometry args={[0.03, 0.03, 0.1]} />
           <meshStandardMaterial color="#1e293b" />
         </mesh>
      </group>
    </Interactive>
  )
}
