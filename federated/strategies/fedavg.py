"""
FedAvg & FedProx Strategy Implementation
Implements standard Federated Averaging (FedAvg) and FedProx (with mu proximal term for non-IID drift).
"""

import numpy as np
from typing import List, Dict, Any, Tuple

class FedAvgStrategy:
    @classmethod
    def aggregate(cls, client_weights_list: List[Tuple[List[np.ndarray], int]]) -> List[np.ndarray]:
        if not client_weights_list:
            return []
        
        total_samples = sum(num_samples for _, num_samples in client_weights_list)
        num_layers = len(client_weights_list[0][0])
        
        avg_weights = [np.zeros_like(client_weights_list[0][0][i]) for i in range(num_layers)]
        
        for weights, num_samples in client_weights_list:
            weight_factor = num_samples / total_samples
            for i in range(num_layers):
                avg_weights[i] += weights[i] * weight_factor

        return avg_weights

class FedProxStrategy(FedAvgStrategy):
    @classmethod
    def compute_proximal_term(cls, local_weights: List[np.ndarray], global_weights: List[np.ndarray], mu: float = 0.01) -> float:
        prox_loss = 0.0
        for lw, gw in zip(local_weights, global_weights):
            prox_loss += np.sum((lw - gw) ** 2)
        return (mu / 2.0) * prox_loss
