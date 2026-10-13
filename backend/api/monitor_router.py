"""
API Router for Point-of-Download Watcher
Provides controls to start/stop watching and fetch active watcher status.
"""

from fastapi import APIRouter
from backend.watcher.download_monitor import download_monitor_instance
from backend.config import DOWNLOADS_WATCH_DIR

router = APIRouter(prefix="/api/monitor", tags=["Download Watcher"])

@router.get("/status")
def get_monitor_status():
    return {
        "is_active": download_monitor_instance.is_running,
        "watch_directory": str(DOWNLOADS_WATCH_DIR)
    }

@router.post("/start")
def start_monitor():
    download_monitor_instance.start()
    return {"status": "success", "message": "Download monitor started successfully.", "is_active": True}

@router.post("/stop")
def stop_monitor():
    download_monitor_instance.stop()
    return {"status": "success", "message": "Download monitor stopped successfully.", "is_active": False}
