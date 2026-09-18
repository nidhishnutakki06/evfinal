import { useSystemState } from '../state/MockState'
import { Line } from '@react-three/drei'
import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'

function FlowLines({ flows }: { flows: Array<{ path: Array<[number,number,number]>, power: number, color: string }> }) {
  const [dashOffset, setDashOffset] = useState(0)
  const accumulated = useRef(0)

  useFrame((_, delta) => {
    accumulated.current -= delta * 4
    setDashOffset(accumulated.current)
  })

  return (
    <>
      {flows.map(({ path, power, color }, i) => {
        const thickness = Math.min(18, Math.max(3, power * 1.5))
        const dashSize = Math.max(0.5, 3 - power * 0.1) 
        
        return (
          <group key={i}>
            {/* Base soft glow line (continuous) */}
            <Line
              points={path}
              color={color}
              lineWidth={thickness * 1.5}
              transparent
              opacity={0.15}
            />
            {/* Core intense dashed energy flow */}
            <Line
              points={path}
              color={color}
              lineWidth={thickness}
              dashed
              dashSize={dashSize}
              dashScale={2}
              dashOffset={dashOffset}
              transparent
              opacity={0.9}
            />
            {/* Inner bright core */}
            <Line
              points={path}
              color="#ffffff"
              lineWidth={thickness * 0.4}
              dashed
              dashSize={dashSize}
              dashScale={2}
              dashOffset={dashOffset}
              transparent
              opacity={0.8}
            />
          </group>
        )
      })}
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
