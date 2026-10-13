"""
Flower NumPy Client Implementation
Implements Flower client interface for local model training and privacy noise injection.
"""

import flwr as fl
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Any
from backend.ml.pipeline import PyTorchMLP
from federated.privacy.differential_privacy import DifferentialPrivacyEngine

class BrowserShieldFlowerClient(fl.client.NumPyClient):
    def __init__(self, client_id: int, X_train: np.ndarray, y_train: np.ndarray, enable_dp: bool = True):
        self.client_id = client_id
        self.X_train = X_train
        self.y_train = y_train
        self.model = PyTorchMLP(input_dim=42)
        self.enable_dp = enable_dp
        self.dp_engine = DifferentialPrivacyEngine(epsilon=1.5)

    def get_parameters(self, config: Dict[str, Any]) -> List[np.ndarray]:
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters: List[np.ndarray]):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters: List[np.ndarray], config: Dict[str, Any]) -> Tuple[List[np.ndarray], int, Dict[str, Any]]:
        self.set_parameters(parameters)
        
        X_t = torch.tensor(self.X_train, dtype=torch.float32)
        y_t = torch.tensor(self.y_train, dtype=torch.float32).unsqueeze(1)
        
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.005)
        criterion = nn.BCELoss()

        self.model.train()
        for epoch in range(5):
            optimizer.zero_grad()
            out = self.model(X_t)
            loss = criterion(out, y_t)
            loss.backward()
            optimizer.step()

        updated_params = self.get_parameters(config)
        
        # Inject Differential Privacy noise if enabled
        if self.enable_dp:
            updated_params = self.dp_engine.add_noise_to_weights(updated_params)

        return updated_params, len(self.X_train), {"client_id": self.client_id}

    def evaluate(self, parameters: List[np.ndarray], config: Dict[str, Any]) -> Tuple[float, int, Dict[str, Any]]:
        self.set_parameters(parameters)
        self.model.eval()
        
        X_t = torch.tensor(self.X_train, dtype=torch.float32)
        y_t = torch.tensor(self.y_train, dtype=torch.float32).unsqueeze(1)
        
        criterion = nn.BCELoss()
        with torch.no_grad():
            out = self.model(X_t)
            loss = float(criterion(out, y_t).item())
            preds = (out.numpy() >= 0.5).astype(int)
            acc = float(np.mean(preds == y_t.numpy()))

        return loss, len(self.X_train), {"accuracy": acc}
