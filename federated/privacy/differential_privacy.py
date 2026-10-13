"""
Differential Privacy Layer
Implements Gaussian noise injection into model weight updates to protect local client privacy during Federated Learning.
Tracks privacy loss budget (epsilon, delta).
"""

import numpy as np
from typing import List, Tuple

class DifferentialPrivacyEngine:
    def __init__(self, epsilon: float = 1.5, delta: float = 1e-5, clip_norm: float = 1.0):
        self.epsilon = epsilon
        self.delta = delta
        self.clip_norm = clip_norm
        self.total_privacy_cost = 0.0

    def add_noise_to_weights(self, weights: List[np.ndarray], noise_scale: float = 0.05) -> List[np.ndarray]:
        noisy_weights = []
        for w in weights:
            # Clip weights to bound sensitivity
            norm = np.linalg.norm(w)
            if norm > self.clip_norm and norm > 0:
                w_clipped = w * (self.clip_norm / norm)
            else:
                w_clipped = w
            
            # Inject Gaussian Noise N(0, (noise_scale * clip_norm)^2)
            noise = np.random.normal(0.0, noise_scale * self.clip_norm, size=w.shape)
            noisy_weights.append(w_clipped + noise)

        self.total_privacy_cost += (self.epsilon * 0.1) # Accumulated privacy consumption
        return noisy_weights

    def get_privacy_budget(self) -> Dict[str, float]:
        return {
            "target_epsilon": self.epsilon,
            "target_delta": self.delta,
            "clip_norm": self.clip_norm,
            "spent_epsilon": round(self.total_privacy_cost, 4)
        }
