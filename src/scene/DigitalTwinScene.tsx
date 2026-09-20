import { OrbitControls } from '@react-three/drei'
import { Ground } from '../components/Ground'
import { Building } from '../components/Building'
import { SolarArray } from '../components/SolarPanel'
import { ChargingShed } from '../components/ChargingShed'
import { ParkingArea } from '../components/ParkingArea'
import { ChargingStation } from '../components/ChargingStation'
import { GridInfrastructure } from '../components/GridInfrastructure'
import { ElectricalWires } from '../components/ElectricalWires'
import { Bike, Hatchback, Scooter, SUV, Sedan } from '../components/EVModels'
import { PowerFlowSystem } from '../components/PowerFlowSystem'
import { WeatherEnvironment } from '../components/WeatherEnvironment'
import { Roads } from '../components/Roads'
import { Landscaping } from '../components/Landscaping'
import { useSystemState } from '../state/MockState'

const STATION_POSITIONS: [number, number, number][] = [
  [-7.5, 0, 7.5],
  [-4.5, 0, 7.5],
  [-1.5, 0, 7.5],
  [1.5, 0, 7.5],
  [4.5, 0, 7.5],
  [7.5, 0, 7.5]
];

const EV_STATION_POSITIONS: [number, number, number][] = [
  [-7.5, 0, 10],
  [-4.5, 0, 10],
  [-1.5, 0, 10],
  [1.5, 0, 10],
  [4.5, 0, 10],
  [7.5, 0, 10]
];

const WAITING_POSITIONS: [number, number, number][] = [
  [14.5, 0, 10],
  [17.5, 0, 10]
];

const EV_COMPONENTS: Record<string, React.FC<any>> = {
  suv: SUV,
  sedan: Sedan,
  hatchback: Hatchback,
  scooter: Scooter,
  bike: Bike
};

export function DigitalTwinScene() {
  const state = useSystemState();

  const stations = state.stations || [];
  const evs = state.evs || [];

  let waitingIndex = 0;

  return (
    <>
      <OrbitControls
        makeDefault
        minDistance={10}
        maxDistance={150}
        maxPolarAngle={Math.PI / 2 - 0.05}
        target={[-2, 0, 8]}
      />

      {/* Dynamic Weather & Time of Day */}
      <WeatherEnvironment />

      {/* Core Ground Foundation */}
      <Ground />

      {/* Campus Road Network */}
      <Roads />

      {/* Landscaping — trees, shrubs, grass */}
      <Landscaping />

      {/* Building Area */}
      <Building position={[0, 0, -25]} />
      <SolarArray id="solar-building" rows={3} cols={6} spacingX={2.2} spacingZ={3.2} position={[0, 21.5, -25]} rotation={[-0.2, 0, 0]} />

      {/* Shed and Parking */}
      <ChargingShed position={[0, 0, 10]} />
      <ParkingArea position={[0, 0, 10]} spots={6} isCharging={true} />
      
      {/* Waiting Area (Non-charging parking spots) on the right side with gap */}
      <ParkingArea position={[16, 0, 10]} spots={2} isCharging={false} />
      
      {/* Charging Stations */}
      {stations.map((st, index) => {
        if (index >= STATION_POSITIONS.length) {
          console.warn(`Station ${st.station_id} exceeds available 3D slots and will not be rendered.`);
          return null;
        }
        return (
          <ChargingStation 
            key={st.station_id} 
            station_id={st.station_id} 
            position={STATION_POSITIONS[index]} 
          />
        );
      })}

      {/* EVs */}
      {evs.map((ev) => {
        const vType = ev.vehicle_type?.toLowerCase() || '';
        const EvComponent = EV_COMPONENTS[vType] || Sedan; // fallback to Sedan
        
        let position: [number, number, number] | null = null;
        
        if (ev.station_id) {
          // Find the station index to map to the EV position
          const stationIndex = stations.findIndex(s => s.station_id === ev.station_id);
          if (stationIndex !== -1 && stationIndex < EV_STATION_POSITIONS.length) {
            position = EV_STATION_POSITIONS[stationIndex];
          }
        } else {
          // Waiting Area
          if (waitingIndex < WAITING_POSITIONS.length) {
            position = WAITING_POSITIONS[waitingIndex];
            waitingIndex++;
          } else {
            console.warn(`Waiting EV ${ev.ev_id} exceeds available waiting slots and will not be rendered.`);
          }
        }

        if (!position) return null;

        return (
          <EvComponent 
            key={ev.ev_id} 
            ev_id={ev.ev_id} 
            position={position} 
            rotation={[0, Math.PI, 0]} 
          />
        );
      })}

      {/* Grid and Transformer */}
      <GridInfrastructure position={[-25, 0, -20]} />

      {/* Floor lines/wires connecting them */}
      <ElectricalWires />

      {/* Animated Power Flows */}
      <PowerFlowSystem />
    </>
  )
}
