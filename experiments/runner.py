"""
Comprehensive Experiment & Ablation Study Orchestrator
Executes Experiments 1-9, Feature Dimensionality Comparison (28-dim vs 42-dim), and 7-Step Feature Ablation Study.
Saves quantitative experimental metrics to results.json.
"""

import os
import json
import numpy as np
from typing import Dict, Any, List

from dataset.dataset_generator import DatasetGenerator
from backend.ml.pipeline import ml_pipeline_instance
from federated.server.fl_server import FLSimulationRunner
from backend.adversarial.robustness_suite import RobustnessSuite

class ExperimentRunner:
    @classmethod
    def run_all_experiments(cls) -> Dict[str, Any]:
        X, y, meta = DatasetGenerator.generate_full_dataset(num_samples_per_cat=50)
        
        # Train-Test Split (80% Train, 20% Test)
        indices = np.arange(len(X))
        np.random.seed(42)
        np.random.shuffle(indices)
        split = int(0.8 * len(X))
        
        train_idx, test_idx = indices[:split], indices[split:]
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]

        # 1. Centralized ML Experiments (LR, RF, XGB, NN)
        centralized_results = ml_pipeline_instance.fit_and_evaluate_all(X_train, y_train, X_test, y_test)

        # 2. Feature Vector Comparison (Original 28-dim paper features vs New 42-dim features)
        feature_comparison = cls._compare_feature_dimensions(X_train, y_train, X_test, y_test)

        # 3. Federated Learning Experiments (FedAvg vs FedProx)
        fedavg_results = FLSimulationRunner.run_simulation(X, y, num_clients=3, num_rounds=5, strategy_name="FedAvg", enable_dp=True)
        fedprox_results = FLSimulationRunner.run_simulation(X, y, num_clients=3, num_rounds=5, strategy_name="FedProx", enable_dp=True)

        # 4. Adversarial Robustness Suite Evaluation
        robustness_res = RobustnessSuite.evaluate_robustness()

        # 5. Feature Ablation Study (Steps A through G)
        ablation_results = cls._run_ablation_study(X_train, y_train, X_test, y_test)

        # Consolidated Benchmark Summary
        experiment_summary = {
            "research_framing": "A multi-layer, explainable and adaptive file-spoofing detection framework that combines binary-content analysis, structural validation, machine learning, adversarial robustness, and privacy-preserving federated learning.",
            "dataset_info": {
                "total_samples": int(len(X)),
                "train_samples": int(len(X_train)),
                "test_samples": int(len(X_test)),
                "num_features": int(X.shape[1])
            },
            "feature_dimension_comparison": feature_comparison,
            "centralized_models": centralized_results,
            "federated_learning": {
                "fedavg": fedavg_results,
                "fedprox": fedprox_results
            },
            "adversarial_robustness": robustness_res,
            "ablation_study": ablation_results
        }

        # Save to file
        output_path = os.path.join(os.path.dirname(__file__), "results.json")
        with open(output_path, "w") as f:
            json.dump(experiment_summary, f, indent=2)

        return experiment_summary

    @classmethod
    def _compare_feature_dimensions(cls, X_tr: np.ndarray, y_tr: np.ndarray, X_te: np.ndarray, y_te: np.ndarray) -> Dict[str, Any]:
        # Original 28-dim paper features (subset of indices)
        indices_28 = list(range(0, 2)) + list(range(10, 18)) + list(range(24, 41)) # 28 features
        X_tr_28, X_te_28 = X_tr[:, indices_28], X_te[:, indices_28]

        from sklearn.ensemble import RandomForestClassifier
        rf28 = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)
        rf28.fit(X_tr_28, y_tr)
        preds28 = rf28.predict(X_te_28)
        probs28 = rf28.predict_proba(X_te_28)[:, 1]
        m28 = ml_pipeline_instance._eval_metrics(y_te, preds28, probs28)

        rf42 = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)
        rf42.fit(X_tr, y_tr)
        preds42 = rf42.predict(X_te)
        probs42 = rf42.predict_proba(X_te)[:, 1]
        m42 = ml_pipeline_instance._eval_metrics(y_te, preds42, probs42)

        return {
            "original_28_dim_paper_features": {
                "num_features": 28,
                "accuracy": m28["accuracy"],
                "f1_score": m28["f1_score"],
                "roc_auc": m28["roc_auc"]
            },
            "new_42_dim_multi_layer_features": {
                "num_features": 42,
                "accuracy": m42["accuracy"],
                "f1_score": m42["f1_score"],
                "roc_auc": m42["roc_auc"]
            },
            "f1_improvement": round(m42["f1_score"] - m28["f1_score"], 4)
        }

    @classmethod
    def _run_ablation_study(cls, X_tr: np.ndarray, y_tr: np.ndarray, X_te: np.ndarray, y_te: np.ndarray) -> Dict[str, Any]:
        ablation_steps = {
            "Step_A_Header_Only": list(range(10, 14)),
            "Step_B_Header_Footer": list(range(10, 18)),
            "Step_C_Header_Footer_Entropy": list(range(2, 18)),
            "Step_D_Add_MIME": list(range(2, 19)),
            "Step_E_Add_Byte_Stats": list(range(2, 40)),
            "Step_F_Add_Structure": list(range(2, 42)),
            "Step_G_Full_Model": list(range(42))
        }

        results = {}
        for name, feat_indices in ablation_steps.items():
            X_tr_sub = X_tr[:, feat_indices]
            X_te_sub = X_te[:, feat_indices]

            from sklearn.ensemble import RandomForestClassifier
            rf = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)
            rf.fit(X_tr_sub, y_tr)
            preds = rf.predict(X_te_sub)
            probs = rf.predict_proba(X_te_sub)[:, 1]

            metrics = ml_pipeline_instance._eval_metrics(y_te, preds, probs)
            results[name] = {
                "num_features_used": len(feat_indices),
                "accuracy": metrics["accuracy"],
                "f1_score": metrics["f1_score"],
                "roc_auc": metrics["roc_auc"]
            }

        return results
