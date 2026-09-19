import { useSystemState } from '../state/MockState'
import { useRef, useMemo, useEffect } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

interface FlowItem {
  path: Array<[number, number, number]>
  power: number
  color: string
}

function SingleFlow({ path, power, color }: FlowItem) {
  const pulseRef1 = useRef<THREE.Mesh>(null)
  const pulseRef2 = useRef<THREE.Mesh>(null)
  const pulseRef3 = useRef<THREE.Mesh>(null)
  const progress = useRef(0)

  const curve = useMemo(() => {
    const c = new THREE.CurvePath<THREE.Vector3>()
    for (let j = 0; j < path.length - 1; j++) {
      c.add(new THREE.LineCurve3(new THREE.Vector3(...path[j]), new THREE.Vector3(...path[j + 1])))
    }
    return c
  }, [path])

  const radius = Math.min(0.12, Math.max(0.04, power * 0.012))

  const { outerGeom, innerGeom } = useMemo(() => {
    const outer = new THREE.TubeGeometry(curve, 32, radius, 8, false)
    const inner = new THREE.TubeGeometry(curve, 32, radius * 0.45, 8, false)
    return { outerGeom: outer, innerGeom: inner }
  }, [curve, radius])

  useEffect(() => {
    return () => {
      outerGeom.dispose()
      innerGeom.dispose()
    }
  }, [outerGeom, innerGeom])

  useFrame((_, delta) => {
    progress.current = (progress.current + delta * 0.6) % 1
    const p1 = progress.current
    const p2 = (progress.current + 0.33) % 1
    const p3 = (progress.current + 0.66) % 1

    if (pulseRef1.current) pulseRef1.current.position.copy(curve.getPointAt(p1))
    if (pulseRef2.current) pulseRef2.current.position.copy(curve.getPointAt(p2))
    if (pulseRef3.current) pulseRef3.current.position.copy(curve.getPointAt(p3))
  })

  return (
    <group>
      {/* Outer glowing conduit */}
      <mesh geometry={outerGeom}>
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={0.6}
          transparent
          opacity={0.35}
          roughness={0.3}
        />
      </mesh>

      {/* Inner bright core */}
      <mesh geometry={innerGeom}>
        <meshBasicMaterial color="#ffffff" transparent opacity={0.75} />
      </mesh>

      {/* Animated traveling energy pulses along the conduit */}
      <mesh ref={pulseRef1}>
        <sphereGeometry args={[radius * 2.0, 8, 8]} />
        <meshBasicMaterial color="#ffffff" />
      </mesh>
      <mesh ref={pulseRef2}>
        <sphereGeometry args={[radius * 2.0, 8, 8]} />
        <meshBasicMaterial color={color} />
      </mesh>
      <mesh ref={pulseRef3}>
        <sphereGeometry args={[radius * 2.0, 8, 8]} />
        <meshBasicMaterial color="#ffffff" />
      </mesh>
    </group>
  )
}

function FlowLines({ flows }: { flows: FlowItem[] }) {
  return (
    <>
      {flows.map((flow, i) => (
        <SingleFlow key={i} {...flow} />
      ))}
    </>
  )
}

export function PowerFlowSystem() {
  const state = useSystemState()

  // EXACT BACKEND MAPPINGS (Preserved from Phase 1-15)
  // Zero/missing kW = no flow rendered.
  const GRID_POS: [number, number, number] = [-25, 0.5, -20]
  const SHED_SOLAR_POS: [number, number, number] = [0, 4.5, 10]

  const STATION_POSITIONS: Record<string, { charger: [number, number, number], ev: [number, number, number] }> = {
    'ST-1': { charger: [-7.5, 1.5, 7.5], ev: [-7.5, 0.5, 10] },
    'ST-2': { charger: [-4.5, 1.5, 7.5], ev: [-4.5, 0.5, 10] },
    'ST-3': { charger: [-1.5, 1.5, 7.5], ev: [-1.5, 0.5, 10] },
    'ST-4': { charger: [1.5, 1.5, 7.5], ev: [1.5, 0.5, 10] },
    'ST-5': { charger: [4.5, 1.5, 7.5], ev: [4.5, 0.5, 10] },
    'ST-6': { charger: [7.5, 1.5, 7.5], ev: [7.5, 0.5, 10] }
  }

  const flows: Array<{ path: Array<[number,number,number]>, power: number, color: string }> = []

  state.evs?.forEach(ev => {
    if (!ev.station_id || !STATION_POSITIONS[ev.station_id]) return
    const { charger, ev: evPos } = STATION_POSITIONS[ev.station_id]

    // Route grid flow along a ground-level path rather than a diagonal line through the sky
    const gridRoute: Array<[number,number,number]> = [
      GRID_POS,
      [-25, 0.5, 10], // route down to the charging strip z-axis
      [evPos[0], 0.5, 10], // route along the strip to the specific EV's x-axis
      evPos
    ]

    const solarRoute: Array<[number,number,number]> = [
      SHED_SOLAR_POS,
      [0, 4.5, 7.5], // route to edge of roof
      [evPos[0], 4.5, 7.5], // route along edge to EV's x-axis
      [evPos[0], 1.5, 7.5], // route down to charger height
      evPos
    ]

    const chargerRoute: Array<[number,number,number]> = [
      charger,
      evPos
    ]

    if ((ev.grid_contribution || 0) > 0)
      flows.push({ path: gridRoute, power: ev.grid_contribution!, color: '#ef4444' }) 
    if ((ev.solar_contribution || 0) > 0)
      flows.push({ path: solarRoute, power: ev.solar_contribution!, color: '#3b82f6' }) 
    if ((ev.current_rate || 0) > 0)
      flows.push({ path: chargerRoute, power: ev.current_rate!, color: '#06b6d4' }) 
  })

  if (flows.length === 0) return null

  return <FlowLines flows={flows} />
}
