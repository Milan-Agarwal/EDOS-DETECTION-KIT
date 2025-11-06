"""
EDoS Security Dashboard Backend
A comprehensive FastAPI backend for real-time cybersecurity monitoring
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid
import random

from app.core.config import settings
from app.core.websocket_manager import ConnectionManager
from app.api import auth, alerts, network, resources, metrics, logs, settings_api
from app.services.data_generator import DataGenerator
from app.models.schemas import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize connection manager and data generator
connection_manager = ConnectionManager()
data_generator = DataGenerator()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting EDoS Security Dashboard Backend")

    # Initialize database
    logger.info("🗄️ Initializing database...")
    try:
        from app.database import initialize_database, check_database_connection

        # Check if database is available
        if check_database_connection():
            logger.info("✅ Database connection established")
        else:
            # Try to initialize database
            success = await initialize_database()
            if success:
                logger.info("✅ Database initialized successfully")
            else:
                logger.warning("⚠️ Database initialization failed, using mock data")
    except Exception as e:
        logger.warning(
            f"⚠️ Database initialization error: {e}, falling back to mock data"
        )

    # Start background tasks for real-time data generation
    background_task = asyncio.create_task(background_data_generator())

    yield

    # Shutdown
    logger.info("🛑 Shutting down EDoS Security Dashboard Backend")
    background_task.cancel()


# Create FastAPI app
app = FastAPI(
    title="EDoS Security Dashboard API",
    description="A comprehensive cybersecurity monitoring and threat detection API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(network.router, prefix="/api/network", tags=["Network"])
app.include_router(resources.router, prefix="/api/resources", tags=["Resources"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(logs.router, prefix="/api/logs", tags=["Logs"])
app.include_router(settings_api.router, prefix="/api/settings", tags=["Settings"])


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "edos-security-dashboard",
        "version": "1.0.0",
    }


# WebSocket endpoints
@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alerts"""
    await connection_manager.connect(websocket, "alerts")
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "alerts")


@app.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """WebSocket endpoint for real-time metrics"""
    await connection_manager.connect(websocket, "metrics")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "metrics")


@app.websocket("/ws/network-traffic")
async def websocket_network_traffic(websocket: WebSocket):
    """WebSocket endpoint for real-time network traffic (3D Globe)"""
    await connection_manager.connect(websocket, "network_traffic")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "network_traffic")


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket endpoint for real-time logs"""
    await connection_manager.connect(websocket, "logs")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, "logs")


# Background task for generating real-time data
async def background_data_generator():
    """Generate real-time data for the dashboard"""
    logger.info("🔄 Starting background data generator")

    while True:
        try:
            # Generate and broadcast alerts (every 10-30 seconds)
            if random.random() < 0.3:  # 30% chance
                alert = data_generator.generate_alert()
                await connection_manager.broadcast(
                    "alerts", {"type": "new_alert", "data": alert.dict()}
                )

            # Generate and broadcast network traffic (every 2-5 seconds)
            if random.random() < 0.8:  # 80% chance
                traffic = data_generator.generate_network_traffic()
                await connection_manager.broadcast(
                    "network_traffic", {"type": "traffic_update", "data": traffic}
                )

            # Generate and broadcast metrics (every 3 seconds)
            metrics_data = data_generator.generate_metrics()
            await connection_manager.broadcast(
                "metrics", {"type": "metrics_update", "data": metrics_data}
            )

            # Generate and broadcast logs (every 2-8 seconds)
            if random.random() < 0.7:  # 70% chance
                log_entry = data_generator.generate_log()
                await connection_manager.broadcast(
                    "logs", {"type": "new_log", "data": log_entry.dict()}
                )

            # Wait before next iteration
            await asyncio.sleep(random.uniform(2, 5))

        except Exception as e:
            logger.error(f"Error in background data generator: {e}")
            await asyncio.sleep(5)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "EDoS Security Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "websockets": {
            "alerts": "/ws/alerts",
            "metrics": "/ws/metrics",
            "network_traffic": "/ws/network-traffic",
            "logs": "/ws/logs",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
