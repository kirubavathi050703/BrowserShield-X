"""
BrowserShield-X Main FastAPI Application Entry Point
"""

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager

# Ensure project root (browser_shield_x) is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.scan_router import router as scan_router
from backend.api.history_router import router as history_router
from backend.api.quarantine_router import router as quarantine_router
from backend.api.monitor_router import router as monitor_router
from backend.api.analytics_router import router as analytics_router
from backend.api.fl_router import router as fl_router
from backend.api.settings_router import router as settings_router

from backend.watcher.download_monitor import download_monitor_instance
from experiments.runner import ExperimentRunner

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[BrowserShield-X] Backend starting up...")
    try:
        results_path = os.path.join(os.path.dirname(__file__), "..", "experiments", "results.json")
        if not os.path.exists(results_path):
            print("[BrowserShield-X] Running initial model training and experiments...")
            ExperimentRunner.run_all_experiments()
    except Exception as e:
        print(f"[BrowserShield-X] Initial training warning: {e}")

    try:
        download_monitor_instance.start()
    except Exception as e:
        print(f"[BrowserShield-X] Monitor start warning: {e}")

    yield

    print("[BrowserShield-X] Backend shutting down...")
    download_monitor_instance.stop()

app = FastAPI(
    title="BrowserShield-X API",
    description="Explainable Multi-Layer Adaptive File Spoofing Detection and Privacy-Preserving Federated Learning Engine",
    version="2.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(scan_router)
app.include_router(history_router)
app.include_router(quarantine_router)
app.include_router(monitor_router)
app.include_router(analytics_router)
app.include_router(fl_router)
app.include_router(settings_router)

@app.get("/")
def root():
    return {
        "system": "BrowserShield-X",
        "status": "OPERATIONAL",
        "version": "2.0.0",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
