"""
API Router for Federated Learning & Differential Privacy
Provides FL simulation triggers and strategy comparisons (FedAvg vs FedProx).
"""

from fastapi import APIRouter, Query
from dataset.dataset_generator import DatasetGenerator
from federated.server.fl_server import FLSimulationRunner
from federated.privacy.differential_privacy import DifferentialPrivacyEngine

router = APIRouter(prefix="/api/fl", tags=["Federated Learning"])

@router.get("/simulate")
def run_fl_simulation(num_rounds: int = Query(5, ge=1, le=20), strategy: str = Query("FedProx", pattern="^(FedAvg|FedProx)$")):
    X, y, _ = DatasetGenerator.generate_full_dataset(num_samples_per_cat=30)
    result = FLSimulationRunner.run_simulation(X, y, num_clients=3, num_rounds=num_rounds, strategy_name=strategy, enable_dp=True)
    
    dp = DifferentialPrivacyEngine()
    dp_info = dp.get_privacy_budget()
    result["privacy_budget"] = dp_info

    return result
