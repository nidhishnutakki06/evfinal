# API Contract

This document explicitly outlines the authoritative REST and WebSocket interfaces for the SH-305 backend. It directly mirrors the FastAPI endpoints implemented on the server. 

**Note on Validation:** 
- If a request body fails type requirements or boundary bounds (e.g. providing a negative grid limit), the server safely rejects it with HTTP `422 Unprocessable Entity`.
- If a structurally sound request violates an internal logical invariant or fails memory assignment, it is rejected with HTTP `400 Bad Request`.

---

## 1. System Health & State Retrieval

### `GET /api/health`
- **Purpose**: Verify backend uptime.
- **Request Body**: None
- **Successful Response** (`200 OK`): `{"status": "ok"}`

### `GET /api/state`
- **Purpose**: Fetch the authoritative `SystemState` snapshot.
- **Request Body**: None
- **Successful Response** (`200 OK`): Full JSON representation of `SystemState`.

---

## 2. Simulation Lifecycle Controls

### `POST /api/simulation/start`
- **Purpose**: Mark the runtime simulation as actively running.
- **Request Body**: None
- **Successful Response** (`200 OK`): Updated `SystemState`

### `POST /api/simulation/pause`
- **Purpose**: Pause the active simulation.
- **Request Body**: None
- **Successful Response** (`200 OK`): Updated `SystemState`

### `POST /api/simulation/reset`
- **Purpose**: Revert the system to its empty initial baseline, maintaining static database definitions and configured grid boundaries.
- **Request Body**: None
- **Successful Response** (`200 OK`): Updated `SystemState`

---

## 3. Configuration & Control Mutations

### `POST /api/control/building-demand`
- **Purpose**: Apply manual or synthesized building energy demands.
- **Request Body**:
  ```json
  {
    "ac": 0.0,
    "lights": 0.0,
    "lifts": 0.0,
    "appliances": 0.0
  }
  ```
  - **Constraints**: All fields are `float`, required, and must be `>= 0.0`.
- **Successful Response** (`200 OK`): Updated `SystemState`

### `POST /api/control/grid-limit`
- **Purpose**: Adjust the standard configured maximum power import from the local grid.
- **Request Body**:
  ```json
  {
    "limit": 500.0
  }
  ```
  - **Constraints**: `limit` must be a `float >= 0.0`.
- **Successful Response** (`200 OK`): Updated `SystemState`

### `POST /api/control/weather`
- **Purpose**: Inject the current weather scenario string.
- **Request Body**:
  ```json
  {
    "weather": "Sunny"
  }
  ```
  - **Constraints**: `weather` is a required `string`.
- **Successful Response** (`200 OK`): Updated `SystemState`

### `POST /api/control/strategy`
- **Purpose**: Override the active dispatch logic guiding EV allocation priorities.
- **Request Body**:
  ```json
  {
    "active_strategy": "DEADLINE_FIRST"
  }
  ```
  - **Constraints**: `active_strategy` must exactly match the Enum string values: `"DEADLINE_FIRST" | "SOLAR_FIRST" | "GRID_SAFETY_FIRST"`.
- **Successful Response** (`200 OK`): Updated `SystemState`

---

## 4. EV Spawning Mechanics

### `POST /api/control/spawn-ev`
- **Purpose**: Introduce a new EV into the canonical simulation.
- **Request Body**:
  ```json
  {
    "ev_id": "EV-123",
    "vehicle_type": "Car",
    "battery_capacity": 50.0,
    "target_soc": 80.0,
    "requested_travel_distance": 100.0,
    "arrival": 0.0,
    "departure": 12.0,
    "minimum_rate": 0.0,
    "maximum_rate": 11.0,
    "station_id": "ST-1"
  }
  ```
- **Fields & Constraints**:
  - `ev_id` (str, required)
  - `vehicle_type` (str, required)
  - `battery_capacity` (float, required, `> 0.0`)
  - `target_soc` (float, required, `>= 0.0`, `<= 100.0`)
  - `requested_travel_distance` (float, optional, `>= 0.0`, default `0.0`)
  - `arrival` (float, required)
  - `departure` (float, required)
  - `minimum_rate` (float, optional, `>= 0.0`, default `0.0`)
  - `maximum_rate` (float, required, `>= 0.0`)
  - `station_id` (str, optional, default `null`)
  - **Logical Invariants Enforced**: `arrival <= departure` and `minimum_rate <= maximum_rate`.
- **Successful Response** (`200 OK`): Updated `SystemState`

### `POST /api/control/spawn-urgent-ev`
- **Purpose**: Spawn an EV with an identical payload to `spawn-ev`, but explicitly forces the `urgency` field to `"URGENT"`.
- **Request Body**: Same as `SpawnEVRequest` above.
- **Successful Response** (`200 OK`): Updated `SystemState`

---

## 5. Emergency Intervention

### `POST /api/control/emergency/activate`
- **Purpose**: Trigger a grid emergency. Instantly limits the `active_limit` to the `emergency_limit`.
- **Request Body**: None
- **Successful Response** (`200 OK`): Updated `SystemState`

### `POST /api/control/emergency/restore`
- **Purpose**: Lift the grid emergency. Reverts the `active_limit` back to the standard `configured_limit`.
- **Request Body**: None
- **Successful Response** (`200 OK`): Updated `SystemState`

---

## 6. WebSocket Realtime Streaming

### `WS /ws/state`
- **Connection**: Standard WebSocket connection directly to the endpoint.
- **Initial Message**: Immediately upon successful handshake, the backend pushes out the entire JSON canonical `SystemState`. You do not need to issue a request payload.
- **Subsequent Messages (Broadcasts)**: Whenever a REST mutation executes successfully on the backend, a fresh `SystemState` JSON string is broadcast unconditionally to all active WebSockets.
- **Disconnect Behavior**: Clients may drop cleanly without bringing down the server or disrupting peer broadcasts.
- **Client Message Behavior**: Sending messages from the frontend through this socket is **intentionally ignored** by the backend. The stream is strictly one-way (Server -> Client) to maintain authoritative integrity. Use the REST API if you wish to mutate state.
