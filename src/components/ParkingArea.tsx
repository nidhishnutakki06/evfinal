import { useMemo } from 'react'

export function ParkingArea({ position = [0, 0, 0], rotation = [0, 0, 0], spots = 6, isCharging = true }: any) {
  const spotWidth = 3
  const spotDepth = 6
  const totalWidth = spots * spotWidth

  // Memoised static geometry — bay lines, tints, stoppers don't change per frame
  const bayLines = useMemo(
    () =>
      Array.from({ length: spots + 1 }, (_, i) => (
        <mesh
          key={`line-${i}`}
          position={[-totalWidth / 2 + i * spotWidth, 0.012, 0]}
          rotation={[-Math.PI / 2, 0, 0]}
        >
          <planeGeometry args={[0.09, spotDepth]} />
          <meshBasicMaterial color="#e8e8e8" transparent opacity={0.75} />
        </mesh>
      )),
    [spots, totalWidth, spotWidth, spotDepth],
  )

  const evBayTints = useMemo(
    () =>
      Array.from({ length: spots }, (_, i) => (
        <mesh
          key={`bay-${i}`}
          position={[-totalWidth / 2 + i * spotWidth + spotWidth / 2, 0.009, 0.5]}
          rotation={[-Math.PI / 2, 0, 0]}
        >
          <planeGeometry args={[spotWidth - 0.15, spotDepth - 1.5]} />
          <meshBasicMaterial color="#003a6e" transparent opacity={0.3} />
        </mesh>
      )),
    [spots, totalWidth, spotWidth, spotDepth],
  )

  const stoppers = useMemo(
    () =>
      Array.from({ length: spots }, (_, i) => (
        <mesh
          key={`stop-${i}`}
          position={[-totalWidth / 2 + i * spotWidth + spotWidth / 2, 0.1, -spotDepth / 2 + 0.55]}
          castShadow
          receiveShadow
        >
          <boxGeometry args={[1.6, 0.2, 0.28]} />
          <meshStandardMaterial color="#cccccc" roughness={0.7} />
        </mesh>
      )),
    [spots, totalWidth, spotWidth, spotDepth],
  )

  return (
    <group position={position} rotation={rotation}>
      {/* Asphalt base */}
      <mesh position={[0, 0.005, 0]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[totalWidth + 1.5, spotDepth + 2.5]} />
        <meshStandardMaterial color="#14161c" roughness={0.92} />
      </mesh>

      {/* Bay divider lines */}
      {bayLines}

      {/* Blue EV-bay tint overlay per spot */}
      {isCharging && evBayTints}

      {/* Front stop line across all bays */}
      <mesh position={[0, 0.012, -spotDepth / 2 + 0.5]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[totalWidth, 0.14]} />
        <meshBasicMaterial color="#dddddd" transparent opacity={0.7} />
      </mesh>

      {/* Direction arrows and charging symbols only for active charging bays */}
      {isCharging && Array.from({ length: spots }, (_, i) => {
        const cx = -totalWidth / 2 + i * spotWidth + spotWidth / 2
        return (
          <group key={`marks-${i}`}>
            <mesh position={[cx, 0.013, 1.2]} rotation={[-Math.PI / 2, 0, 0]}>
              <planeGeometry args={[0.14, 1.2]} />
              <meshBasicMaterial color="#9999bb" transparent opacity={0.55} />
            </mesh>
            <mesh position={[cx, 0.013, -1.2]} rotation={[-Math.PI / 2, 0, 0]}>
              <planeGeometry args={[0.45, 0.55]} />
              <meshBasicMaterial color="#0077cc" transparent opacity={0.55} />
            </mesh>
          </group>
        )
      })}

      {/* Wheel stoppers */}
      {stoppers}
    </group>
  )
}
