// Campus road network — purely visual geometry, no SystemState data consumed.
// Main road runs east-west at z=20 (between camera and charging area).
// Entry driveway runs north-south from z=8.5 → z=16.5 at x=0.
// West access road connects the grid/transformer area to the main road.

export function Roads() {
  return (
    <group>
      {/* ── MAIN CAMPUS ROAD ─────────────────────────────────────────────────
          Centre at z=20, width 7 m (z: 16.5 – 23.5), spans x: ±50          */}
      <mesh position={[0, 0.01, 20]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[100, 7]} />
        <meshStandardMaterial color="#252830" roughness={0.92} metalness={0.08} />
      </mesh>

      {/* White edge lines */}
      <mesh position={[0, 0.016, 16.6]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[100, 0.2]} />
        <meshBasicMaterial color="#d0d0d0" />
      </mesh>
      <mesh position={[0, 0.016, 23.4]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[100, 0.2]} />
        <meshBasicMaterial color="#d0d0d0" />
      </mesh>

      {/* Yellow centre-lane dashes */}
      {Array.from({ length: 22 }, (_, i) => (
        <mesh key={i} position={[-48 + i * 4.5, 0.016, 20]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[2.5, 0.15]} />
          <meshBasicMaterial color="#d4c040" transparent opacity={0.85} />
        </mesh>
      ))}

      {/* Kerb strips (north + south road edges) */}
      <mesh position={[0, 0.06, 16.3]} castShadow receiveShadow>
        <boxGeometry args={[100, 0.12, 0.28]} />
        <meshStandardMaterial color="#5c6070" roughness={0.8} />
      </mesh>
      <mesh position={[0, 0.06, 23.7]} castShadow receiveShadow>
        <boxGeometry args={[100, 0.12, 0.28]} />
        <meshStandardMaterial color="#5c6070" roughness={0.8} />
      </mesh>

      {/* ── PEDESTRIAN CROSSING at campus entry (x = 0) ────────────────────── */}
      {Array.from({ length: 7 }, (_, i) => (
        <mesh key={i} position={[0, 0.018, 17.5 + i * 0.62]} rotation={[-Math.PI / 2, 0, 0]}>
          <planeGeometry args={[6, 0.38]} />
          <meshBasicMaterial color="#ddd" transparent opacity={0.6} />
        </mesh>
      ))}

      {/* ── ENTRY DRIVEWAY ─────────────────────────────────────────────────
          Connects main road to parking base (z: 14.25 → 16.5)   */}
      <mesh position={[0, 0.01, 15.375]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[6, 2.25]} />
        <meshStandardMaterial color="#252830" roughness={0.92} metalness={0.08} />
      </mesh>

      {/* Driveway side edge markings */}
      <mesh position={[-3, 0.016, 15.375]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[0.12, 2.25]} />
        <meshBasicMaterial color="#cccccc" transparent opacity={0.6} />
      </mesh>
      <mesh position={[3, 0.016, 15.375]} rotation={[-Math.PI / 2, 0, 0]}>
        <planeGeometry args={[0.12, 2.25]} />
        <meshBasicMaterial color="#cccccc" transparent opacity={0.6} />
      </mesh>

      {/* ── WEST ACCESS ROAD ───────────────────────────────────────────────
          North-south at x = -22, connects grid/transformer to main road (stops at z=16.5) */}
      <mesh position={[-22, 0.01, -3.75]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[5, 40.5]} />
        <meshStandardMaterial color="#252830" roughness={0.92} metalness={0.08} />
      </mesh>

      {/* ── MAIN CAMPUS PLAZA / CHARGING COURTYARD ───────────────────────────
          Connects the building entrance directly to the charging/parking area 
          Stops exactly at the parking base z=5.75 to prevent z-fighting */}
      <mesh position={[0, 0.005, -5.875]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[38, 23.25]} />
        <meshStandardMaterial color="#252830" roughness={0.92} metalness={0.08} />
      </mesh>
      
      {/* Simple courtyard markings / pathways */}
      <mesh position={[0, 0.008, -5.875]} rotation={[-Math.PI / 2, 0, 0]} receiveShadow>
        <planeGeometry args={[38, 0.1]} />
        <meshBasicMaterial color="#444" transparent opacity={0.6} />
      </mesh>
    </group>
  )
}
