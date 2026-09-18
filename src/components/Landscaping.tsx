import { useMemo } from 'react'

// ── Primitives ──────────────────────────────────────────────────────────────

const FOLIAGE_COLORS = ['#1a5c2a', '#145225', '#1e6830', '#0f4a1e']

/** Two-tier evergreen tree: wide lower cone + narrower upper cone + cylinder trunk */
function Tree({
  position,
  scale = 1,
  colorIndex = 0,
}: {
  position: [number, number, number]
  scale?: number
  colorIndex?: number
}) {
  const color = FOLIAGE_COLORS[colorIndex % FOLIAGE_COLORS.length]
  return (
    <group position={position} scale={scale}>
      {/* Trunk */}
      <mesh position={[0, 0.8, 0]} castShadow receiveShadow>
        <cylinderGeometry args={[0.1, 0.16, 1.6, 8]} />
        <meshStandardMaterial color="#5c3d1e" roughness={0.9} />
      </mesh>
      {/* Lower foliage cone */}
      <mesh position={[0, 2.4, 0]} castShadow>
        <coneGeometry args={[1.0, 2.2, 8]} />
        <meshStandardMaterial color={color} roughness={0.85} />
      </mesh>
      {/* Upper foliage cone */}
      <mesh position={[0, 3.5, 0]} castShadow>
        <coneGeometry args={[0.65, 1.6, 8]} />
        <meshStandardMaterial color={color} roughness={0.85} />
      </mesh>
    </group>
  )
}

/** Round shrub: squashed sphere */
function Shrub({
  position,
  scale = 1,
}: {
  position: [number, number, number]
  scale?: number
}) {
  return (
    <mesh position={position} scale={[scale, scale * 0.55, scale]} castShadow>
      <sphereGeometry args={[0.5, 8, 6]} />
      <meshStandardMaterial color="#2d6e3e" roughness={0.9} />
    </mesh>
  )
}

/** Flat grass patch — receives shadows */
function GrassPatch({
  position,
  width,
  depth,
}: {
  position: [number, number, number]
  width: number
  depth: number
}) {
  return (
    <mesh position={position} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
      <planeGeometry args={[width, depth]} />
      <meshStandardMaterial color="#1c4a26" roughness={1} />
    </mesh>
  )
}

// ── Static placement data ────────────────────────────────────────────────────

// [x, z, scale, colorIndex]
type TreeDef = [number, number, number, number]

const TREE_DEFS: TreeDef[] = [
  // South tree-line (beyond the main road from campus view)
  [-38, 26, 0.9, 0], [-30, 25, 1.0, 1], [-22, 26, 0.85, 2],
  [-14, 25, 1.0, 3], [-6, 26, 0.9, 0],
  [6, 26, 1.0, 1], [14, 25, 0.9, 2],
  [22, 26, 1.0, 3], [30, 25, 0.85, 0], [38, 26, 1.0, 1],
  // East / west road flanks
  [-36, 16, 0.85, 2], [36, 16, 0.9, 3],
  // Building left and right flanks
  [-17, -14, 1.1, 0], [-17, -32, 1.0, 2],
  [17, -14, 1.0, 1], [17, -32, 0.9, 3],
  // Northwest (near grid/transformer)
  [-30, -20, 0.9, 2], [-20, -28, 0.85, 0],
  // East campus edge
  [38, 5, 1.0, 1], [38, -8, 0.9, 2], [38, -18, 1.0, 3],
]

// [x, z, scale]
type ShrubDef = [number, number, number]

const SHRUB_DEFS: ShrubDef[] = [
  // Building entrance
  [-7, -14, 1.0], [7, -14, 1.0], [-10, -14, 0.75], [10, -14, 0.75],
  // Road west edge
  [-36, 13, 0.85], [-33, 13, 0.8],
  // Road east edge
  [33, 13, 0.85], [36, 13, 0.8],
  // Grid area
  [-28, -17, 0.8], [-28, -22, 0.75],
]

// ── Main export ──────────────────────────────────────────────────────────────

export function Landscaping() {
  // Memoised so tree/shrub elements are not recreated on every render
  const trees = useMemo(
    () =>
      TREE_DEFS.map(([x, z, scale, ci], i) => (
        <Tree key={i} position={[x, 0, z]} scale={scale} colorIndex={ci} />
      )),
    [],
  )

  const shrubs = useMemo(
    () =>
      SHRUB_DEFS.map(([x, z, scale], i) => (
        <Shrub key={i} position={[x, 0.28, z]} scale={scale} />
      )),
    [],
  )

  return (
    <group>
      {/* Grass zones — precisely calculated to fit outside all road/parking bounding boxes without overlapping */}
      
      {/* South of Main Road */}
      <GrassPatch position={[0, 0.005, 31.75]} width={100} depth={16.5} />
      
      {/* East of Parking/Plaza, North of Main Road */}
      <GrassPatch position={[34.875, 0.005, -6.75]} width={30.25} depth={46.5} />
      
      {/* Between Plaza and West Access Road */}
      <GrassPatch position={[-19.25, 0.005, -6.75]} width={0.5} depth={46.5} />
      
      {/* West of West Access Road, North of Main Road */}
      <GrassPatch position={[-37.25, 0.005, -6.75]} width={25.5} depth={46.5} />
      
      {/* Median gap between Main Parking and Waiting Parking */}
      <GrassPatch position={[11, 0.005, 10]} width={2.5} depth={8.5} />

      {/* East of Entry Driveway (z=14.25 to 16.5, x=3 to 19.75) */}
      <GrassPatch position={[11.375, 0.005, 15.375]} width={16.75} depth={2.25} />
      
      {/* West of Entry Driveway (z=14.25 to 16.5, x=-19 to -3) */}
      <GrassPatch position={[-11, 0.005, 15.375]} width={16} depth={2.25} />

      {trees}
      {shrubs}
    </group>
  )
}
