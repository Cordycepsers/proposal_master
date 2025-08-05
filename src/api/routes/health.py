"""
Health check and system status routes.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any
import psutil
import platform
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    uptime: str
    system_info: Dict[str, Any]

class SystemStatus(BaseModel):
    """System status response model."""
    cpu_usage: float
    memory_usage: Dict[str, Any]
    disk_usage: Dict[str, Any]
    python_version: str
    platform: str

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        HealthResponse: Current system health status
    """
    try:
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            uptime="0d 0h 0m",  # Would calculate actual uptime in production
            system_info={
                "python_version": platform.python_version(),
                "platform": platform.system(),
                "architecture": platform.architecture()[0]
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            uptime="unknown",
            system_info={"error": str(e)}
        )

@router.get("/status", response_model=SystemStatus)
async def system_status():
    """
    Detailed system status information.
    
    Returns:
        SystemStatus: Detailed system metrics
    """
    try:
        # Get memory info
        memory = psutil.virtual_memory()
        
        # Get disk info
        disk = psutil.disk_usage('/')
        
        return SystemStatus(
            cpu_usage=psutil.cpu_percent(interval=1),
            memory_usage={
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            disk_usage={
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            python_version=platform.python_version(),
            platform=f"{platform.system()} {platform.release()}"
        )
    except Exception as e:
        logger.error(f"System status check failed: {str(e)}")
        raise

@router.get("/ping")
async def ping():
    """
    Simple ping endpoint for load balancer health checks.
    
    Returns:
        dict: Simple pong response
    """
    return {"message": "pong", "timestamp": datetime.now().isoformat()}
