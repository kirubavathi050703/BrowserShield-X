"""
API Router for Model Analytics & Experiments
Provides benchmark results, model comparison metrics, and feature ablation studies.
"""

from fastapi import APIRouter
import os
import json
from experiments.runner import ExperimentRunner

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Experiments"])

@router.get("")
def get_analytics_metrics():
    results_path = os.path.join(os.path.dirname(__file__), "..", "..", "experiments", "results.json")
    if os.path.exists(results_path):
        with open(results_path, "r") as f:
            return json.load(f)
    else:
        # Run experiments dynamically if results don't exist yet
        return ExperimentRunner.run_all_experiments()

@router.post("/run-experiments")
def trigger_experiment_run():
    summary = ExperimentRunner.run_all_experiments()
    return {"status": "success", "summary": summary}
