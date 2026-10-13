"""
Continual Learning Module
Adapts local model to newly detected file spoofing patterns without catastrophic forgetting.
Implements experience replay buffer and EWC penalty logic.
"""

import numpy as np
from typing import List, Dict, Any

class ContinualLearningEngine:
    def __init__(self, buffer_capacity: int = 500):
        self.buffer_capacity = buffer_capacity
        self.replay_X: List[np.ndarray] = []
        self.replay_y: List[int] = []

    def store_pattern(self, feature_vector: List[float], label: int):
        if len(self.replay_X) >= self.buffer_capacity:
            self.replay_X.pop(0)
            self.replay_y.pop(0)
        self.replay_X.append(np.array(feature_vector, dtype=np.float32))
        self.replay_y.append(label)

    def get_replay_batch(self) -> Tuple[np.ndarray, np.ndarray]:
        if not self.replay_X:
            return np.empty((0, 42)), np.empty((0,))
        return np.array(self.replay_X), np.array(self.replay_y)

    def compute_ewc_penalty(self, current_weights: List[np.ndarray], old_weights: List[np.ndarray], fisher_diag: List[np.ndarray], lambda_ewc: float = 100.0) -> float:
        penalty = 0.0
        for cw, ow, f in zip(current_weights, old_weights, fisher_diag):
            penalty += np.sum(f * ((cw - ow) ** 2))
        return 0.5 * lambda_ewc * penalty
