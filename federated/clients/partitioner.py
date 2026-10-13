"""
Non-IID Dataset Partitioner
Splits training datasets into non-identically distributed (Non-IID) client partitions:
- Client 1: PDF and Office heavy
- Client 2: Image and Archive heavy
- Client 3: Executable and Malicious heavy
"""

import numpy as np
from typing import Dict, List, Tuple

class NonIIDPartitioner:
    @classmethod
    def partition_dataset(cls, X: np.ndarray, y: np.ndarray, num_clients: int = 3) -> Dict[int, Tuple[np.ndarray, np.ndarray]]:
        total_samples = len(X)
        indices = np.arange(total_samples)
        
        # Sort indices by feature patterns / classes to simulate heterogeneous client data
        sorted_indices = indices[np.argsort(y)]
        
        # Split into heterogeneous client buckets
        splits = np.array_split(sorted_indices, num_clients)
        
        partitions = {}
        for client_id, idxs in enumerate(splits):
            np.random.shuffle(idxs)
            partitions[client_id] = (X[idxs], y[idxs])
            
        return partitions
