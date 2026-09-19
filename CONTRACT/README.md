# SH-305 Backend Integration Guide

Welcome to the SH-305 Contract Handoff Package. This directory contains the authoritative state contract and API documentation required for Frontend and 3D Teams to integrate with the backend.

## Purpose of this Package
This package explicitly documents the stable boundaries of the backend engine. The backend serves as the absolute authority for the energy and simulation state. 

Frontend and 3D teams **should not**:
- Inspect or depend on internal Python modules.
- Directly query the SQLite database.
- Create duplicate frontend-specific state representations.

## SystemState Authority
The core contract is the `SystemState`. There is exactly **ONE** canonical `SystemState`.
- **REST** (`GET /api/state`) and **WebSocket** (`/ws/state`) use the exact same state structure.
- The state should be consumed as the absolute truth for rendering the UI and 3D dashboard.

## Input vs. Derived Values

### Input Values
Input values are source values provided by the frontend to the backend via documented REST endpoints. Examples include building AC demand, user-defined EV spawn parameters (battery capacity, target SoC), and grid limits.

### Backend-Derived Values
The backend optimization and simulation engines own all derived calculations. **Do not** compute these values on the frontend. Render them directly from the `SystemState`. 
Authoritative derived fields include:
- `allocation`
- `priority_score`
- `energy_required`, `time_remaining`, `required_average_power`
- `estimated_completion`, `estimated_soc_at_departure`, `deadline_status`
- `physical_feasibility`, `current_allocation_feasibility`
- `a3_risk`, `a2_reason`
- `grid_contribution`, `solar_contribution`
- Global energy values: `grid_import`, `usable_solar`, `excess_solar`, `SITE_LOAD`

## Energy Semantics
The backend adheres exactly to the master energy model:
- `B` = building demand
- `P_total` = total EV charging demand
- `S` = solar generation
- `G` = active grid limit

Formulas governing the system natively applied by the backend:
- `SITE_LOAD = B + P_total`
- `USABLE_SOLAR = min(S, SITE_LOAD)`
- `EXCESS_SOLAR = max(0, S - SITE_LOAD)`
- `GRID_IMPORT = max(0, SITE_LOAD - USABLE_SOLAR)`

**Safety Invariant:** `GRID_IMPORT <= G`

## Recommended Integration Workflow
1. **Initial Load**: Fetch the full state using `GET /api/state` to initialize the UI/3D space.
2. **Realtime Updates**: Establish a WebSocket connection to `ws://<host>:<port>/ws/state`. The backend will automatically broadcast the canonical `SystemState` whenever a mutation occurs. Listen to this stream to fluidly update visuals.
3. **Control Interventions**: Use the documented REST endpoints (`POST /api/control/...`) to submit configuration changes. Do not send messages over the WebSocket.

## Example Integration
### 1. Fetch Initial State (REST)
```javascript
const response = await fetch('http://localhost:8000/api/state');
const state = await response.json();
renderDashboard(state);
```

### 2. Connect Realtime Stream (WebSocket)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/state');

ws.onmessage = (event) => {
    // The payload is identical to the REST GET /api/state response.
    const updatedState = JSON.parse(event.data);
    updateDashboard(updatedState);
};
```

### 3. Mutate State (REST)
```javascript
// Spawn a new EV into the system
await fetch('http://localhost:8000/api/control/spawn-ev', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        ev_id: "EV-100",
        vehicle_type: "Car",
        battery_capacity: 50.0,
        target_soc: 80.0,
        requested_travel_distance: 100.0,
        arrival: 0.0,
        departure: 12.0,
        minimum_rate: 0.0,
        maximum_rate: 11.0,
        station_id: "ST-1"
    })
});
// You do not need to fetch the state again; the WebSocket will broadcast the update instantly.
```

## Available Resources
- `API_CONTRACT.md`: Detailed specifications of every available endpoint.
- `SYSTEM_STATE_SCHEMA.json`: The machine-readable JSON Schema for the canonical Pydantic model.
- `EXAMPLE_SYSTEM_STATE.json`: A valid, populated example of the backend's data serialization.
- **OpenAPI**: When the backend is running, interactive API documentation is available at `/docs` (Swagger UI) or `/openapi.json`.
