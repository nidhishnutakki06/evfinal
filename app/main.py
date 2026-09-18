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

# Include the routers
app.include_router(api_router)
app.include_router(ws_router)
