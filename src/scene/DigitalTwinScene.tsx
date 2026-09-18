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

export function DigitalTwinScene() {
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
      <ChargingStation station_id="ST-1" position={[-7.5, 0, 7.5]} />
      <ChargingStation station_id="ST-2" position={[-4.5, 0, 7.5]} />
      <ChargingStation station_id="ST-3" position={[-1.5, 0, 7.5]} />
      <ChargingStation station_id="ST-4" position={[1.5, 0, 7.5]} />
      <ChargingStation station_id="ST-5" position={[4.5, 0, 7.5]} />
      <ChargingStation station_id="ST-6" position={[7.5, 0, 7.5]} />

      {/* EVs parked at the stations */}
      <SUV ev_id="EV-1" position={[-7.5, 0, 10]} rotation={[0, Math.PI, 0]} />
      <Sedan ev_id="ev_002" position={[-4.5, 0, 10]} rotation={[0, Math.PI, 0]} />
      <Hatchback ev_id="ev_003" position={[-1.5, 0, 10]} rotation={[0, Math.PI, 0]} />
      <Scooter ev_id="ev_004" position={[1.5, 0, 10]} rotation={[0, Math.PI, 0]} />
      <Bike ev_id="ev_005" position={[4.5, 0, 10]} rotation={[0, Math.PI, 0]} />
      <Sedan ev_id="ev_006" position={[7.5, 0, 10]} rotation={[0, Math.PI, 0]} />

      {/* Waiting EVs parked neatly in the non-charging bays on the right */}
      <SUV ev_id="ev_007" position={[14.5, 0, 10]} rotation={[0, Math.PI, 0]} />
      <Hatchback ev_id="ev_008" position={[17.5, 0, 10]} rotation={[0, Math.PI, 0]} />

      {/* Grid and Transformer */}
      <GridInfrastructure position={[-25, 0, -20]} />

      {/* Floor lines/wires connecting them */}
      <ElectricalWires />

      {/* Animated Power Flows */}
      <PowerFlowSystem />
    </>
  )
}
