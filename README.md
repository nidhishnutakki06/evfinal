# SH-305 Backend

This repository implements the backend services for SH-305 (Smart EV Charging & Localised Grid Management).

## Architecture

The backend consists of:
1. **Canonical Pydantic Contracts**: Foundational data structures enforcing structural properties.
2. **Persistence Layer**: SQLite + SQLAlchemy definitions for EV, Station, and Scenario configuration.
3. **Runtime State Manager**: Thread-safe memory container acting as the authoritative source of live `SystemState`.
4. **REST API Layer**: Externally facing FastAPI endpoints.

## REST API Contract
The backend exposes the following stable API surface:

### Core Endpoints
- `GET /api/health` - Health check.
- `GET /api/state` - Retrieves the authoritative canonical `SystemState` (JSON).

### Simulation Lifecycle
- `POST /api/simulation/start`
- `POST /api/simulation/pause`
- `POST /api/simulation/reset`

### Control Mutations
- `POST /api/control/building-demand`: Accepts `{"ac": float, "lights": float, "lifts": float, "appliances": float}`
- `POST /api/control/grid-limit`: Accepts `{"limit": float}`
- `POST /api/control/weather`: Accepts `{"weather": str}`
- `POST /api/control/strategy`: Accepts `{"active_strategy": "DEADLINE_FIRST" | "SOLAR_FIRST" | "GRID_SAFETY_FIRST"}`

### EV Management
- `POST /api/control/spawn-ev`: Accepts detailed EV bounds (`ev_id`, `battery_capacity`, `target_soc`, `arrival`, `departure`, `minimum_rate`, `maximum_rate`, etc.).
- `POST /api/control/spawn-urgent-ev`: Same as above, but explicitly assigns `"URGENT"` urgency.

### Emergency Interventions
- `POST /api/control/emergency/activate`
- `POST /api/control/emergency/restore`

*Note: All REST requests communicate directly with the RuntimeStateManager. Malformed data is structurally rejected with a 422 HTTP Code. Invalid state transitions (violating constraints) are safely rejected with a 400 HTTP Code.*

## WebSocket Realtime Contract
The backend pushes realtime updates using WebSockets to ensure visualizations remain synchronized.

### Endpoint
- `ws://<host>:<port>/ws/state`

### Behavior
1. **Initial Connection**: Upon successful connection, the server immediately sends the current canonical `SystemState` exactly as it would appear via `GET /api/state`. 
2. **Broadcasts**: Whenever a REST endpoint successfully mutates the state, the updated `SystemState` is automatically broadcasted to all connected clients.
3. **Client Messages**: The backend currently treats the WebSocket as a strict **server-to-client** stream. Any messages or control commands sent from the client over WebSocket are safely ignored to protect the authoritative system state.
4. **Disconnects**: Clients can safely disconnect without causing server instability. 

### REST vs WebSocket Relationship
Both REST `GET /api/state` and WebSocket `/ws/state` utilize the exact same underlying canonical Pydantic model. 
- You do not need to parse different schemas.
- WebSocket payloads contain the complete `SystemState` structure unconditionally.
- Controls belong strictly to the REST API endpoints.
