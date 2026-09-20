from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.rest import router as api_router
from app.api.websocket import router as ws_router

app = FastAPI(
    title="SH-305 Backend API",
    description="Authoritative backend REST contract for Smart EV Charging.",
    version="1.0.0"
)

# CORS configuration for frontend/3D integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import asyncio
from app.api.deps import control_service
from app.api.websocket import connection_manager

# Include the routers
app.include_router(api_router)
app.include_router(ws_router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulation_tick_loop())

async def simulation_tick_loop():
    import traceback
    while True:
        await asyncio.sleep(1.0)
        try:
            state = control_service.state_manager.get_state()
            if state.simulation.is_running:
                dt = getattr(state.simulation, "timestep", 0.25)
                for ev in state.evs:
                    if ev.station_id and getattr(ev, "current_rate", 0.0) > 0.0:
                        energy_added = ev.current_rate * dt
                        soc_added = (energy_added / ev.battery_capacity) * 100.0
                        ev.current_soc = min(100.0, ev.current_soc + soc_added)
                        if ev.current_soc >= ev.target_soc:
                            ev.current_rate = 0.0
                new_state = control_service._orchestrate(state)
                await connection_manager.broadcast_state(new_state)
        except Exception as e:
            print("SIMULATION TICK ERROR:", e)
            traceback.print_exc()
