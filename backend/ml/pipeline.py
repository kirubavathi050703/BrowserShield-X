"""
Machine Learning Pipeline Module
Manages training, evaluation, inference, and dynamic selection across 4 ML models:
1. Logistic Regression
2. Random Forest Classifier
3. XGBoost Classifier (optional fallback if missing)
4. PyTorch MLP Neural Network (optional fallback if missing)
"""

import os
import joblib
import numpy as np
import warnings
from typing import Dict, Any, List, Tuple

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*InconsistentVersionWarning.*")

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    XGBClassifier = None
    HAS_XGBOOST = False

try:
    import torch
    import torch.nn as nn
    HAS_TORCH = True
    
    class PyTorchMLP(nn.Module):
        def __init__(self, input_dim: int = 42):
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_dim, 64),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.Linear(32, 1),
                nn.Sigmoid()
            )

        def forward(self, x):
            return self.net(x)

except ImportError:
    torch = None
    nn = None
    PyTorchMLP = None
    HAS_TORCH = False

from backend.config import MODELS_DIR

class MLPipeline:
    def __init__(self, models_dir: str = str(MODELS_DIR)):
        self.models_dir = models_dir
        self.lr_model = None
        self.rf_model = None
        self.xgb_model = None
        self.nn_model = None
        self.selected_model_name = "RandomForest"
        self._load_or_init_models()

    def _load_or_init_models(self):
        rf_path = os.path.join(self.models_dir, "rf_model.joblib")
        lr_path = os.path.join(self.models_dir, "lr_model.joblib")
        xgb_path = os.path.join(self.models_dir, "xgb_model.joblib")
        nn_path = os.path.join(self.models_dir, "nn_model.pt")

        if os.path.exists(rf_path):
            self.rf_model = joblib.load(rf_path)
        else:
            self.rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)

        if os.path.exists(lr_path):
            self.lr_model = joblib.load(lr_path)
        else:
            self.lr_model = LogisticRegression(max_iter=1000, random_state=42)

        if HAS_XGBOOST:
            if os.path.exists(xgb_path):
                self.xgb_model = joblib.load(xgb_path)
            else:
                self.xgb_model = XGBClassifier(n_estimators=100, max_depth=6, random_state=42, eval_metric='logloss')

        if HAS_TORCH and PyTorchMLP is not None:
            self.nn_model = PyTorchMLP(input_dim=42)
            if os.path.exists(nn_path):
                try:
                    self.nn_model.load_state_dict(torch.load(nn_path, weights_only=True))
                    self.nn_model.eval()
                except Exception:
                    pass

    def fit_and_evaluate_all(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        results = {}

        # 1. Logistic Regression
        self.lr_model.fit(X_train, y_train)
        lr_preds = self.lr_model.predict(X_test)
        lr_probs = self.lr_model.predict_proba(X_test)[:, 1]
        results["LogisticRegression"] = self._eval_metrics(y_test, lr_preds, lr_probs)
        joblib.dump(self.lr_model, os.path.join(self.models_dir, "lr_model.joblib"))

        # 2. Random Forest
        self.rf_model.fit(X_train, y_train)
        rf_preds = self.rf_model.predict(X_test)
        rf_probs = self.rf_model.predict_proba(X_test)[:, 1]
        results["RandomForest"] = self._eval_metrics(y_test, rf_preds, rf_probs)
        joblib.dump(self.rf_model, os.path.join(self.models_dir, "rf_model.joblib"))

        # 3. XGBoost
        if HAS_XGBOOST and self.xgb_model is not None:
            self.xgb_model.fit(X_train, y_train)
            xgb_preds = self.xgb_model.predict(X_test)
            xgb_probs = self.xgb_model.predict_proba(X_test)[:, 1]
            results["XGBoost"] = self._eval_metrics(y_test, xgb_preds, xgb_probs)
            joblib.dump(self.xgb_model, os.path.join(self.models_dir, "xgb_model.joblib"))

        # 4. PyTorch Neural Network
        if HAS_TORCH and self.nn_model is not None:
            X_t = torch.tensor(X_train, dtype=torch.float32)
            y_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
            optimizer = torch.optim.Adam(self.nn_model.parameters(), lr=0.005)
            criterion = nn.BCELoss()

            self.nn_model.train()
            for epoch in range(50):
                optimizer.zero_grad()
                out = self.nn_model(X_t)
                loss = criterion(out, y_t)
                loss.backward()
                optimizer.step()

            self.nn_model.eval()
            with torch.no_grad():
                nn_probs = self.nn_model(torch.tensor(X_test, dtype=torch.float32)).numpy().squeeze()
                nn_preds = (nn_probs >= 0.5).astype(int)
            
            results["NeuralNetwork"] = self._eval_metrics(y_test, nn_preds, nn_probs)
            torch.save(self.nn_model.state_dict(), os.path.join(self.models_dir, "nn_model.pt"))

        # Select best model based on F1 Score
        best_name = max(results.keys(), key=lambda k: results[k]["f1_score"])
        self.selected_model_name = best_name
        results["best_model"] = best_name

        return results

    def _eval_metrics(self, y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        try:
            auc = roc_auc_score(y_true, y_prob)
        except Exception:
            auc = 0.5
        
        fp = np.sum((y_pred == 1) & (y_true == 0))
        tn = np.sum((y_pred == 0) & (y_true == 0))
        fn = np.sum((y_pred == 0) & (y_true == 1))
        tp = np.sum((y_pred == 1) & (y_true == 1))

        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        return {
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "roc_auc": round(float(auc), 4),
            "fpr": round(float(fpr), 4),
            "fnr": round(float(fnr), 4)
        }

    def predict_probability(self, feature_vector: List[float]) -> Tuple[float, float, str]:
        x = np.array([feature_vector], dtype=np.float32)
        
        if self.selected_model_name == "RandomForest" and hasattr(self.rf_model, "classes_"):
            prob = float(self.rf_model.predict_proba(x)[0, 1])
        elif HAS_XGBOOST and self.selected_model_name == "XGBoost" and hasattr(self.xgb_model, "classes_"):
            prob = float(self.xgb_model.predict_proba(x)[0, 1])
        elif self.selected_model_name == "LogisticRegression" and hasattr(self.lr_model, "classes_"):
            prob = float(self.lr_model.predict_proba(x)[0, 1])
        elif HAS_TORCH and self.nn_model is not None:
            self.nn_model.eval()
            with torch.no_grad():
                prob = float(self.nn_model(torch.tensor(x, dtype=torch.float32)).item())
        else:
            # Fallback to Random Forest if selected model is unavailable
            if hasattr(self.rf_model, "classes_"):
                prob = float(self.rf_model.predict_proba(x)[0, 1])
            else:
                prob = 0.5

        confidence = round(abs(prob - 0.5) * 2.0, 4)
        return round(prob, 4), confidence, self.selected_model_name

# Singleton ML instance
ml_pipeline_instance = MLPipeline()
