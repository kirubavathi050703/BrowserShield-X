"""
Flower Federated Learning Server & Simulation Runner
Runs FL rounds comparing FedAvg vs FedProx under Non-IID client distributions.
"""

import numpy as np
from typing import Dict, Any, List
from federated.clients.partitioner import NonIIDPartitioner
from federated.clients.client_factory import BrowserShieldFlowerClient
from federated.strategies.fedavg import FedAvgStrategy, FedProxStrategy

class FLSimulationRunner:
    @classmethod
    def run_simulation(cls, X: np.ndarray, y: np.ndarray, num_clients: int = 3, num_rounds: int = 5, strategy_name: str = "FedAvg", enable_dp: bool = True) -> Dict[str, Any]:
        partitions = NonIIDPartitioner.partition_dataset(X, y, num_clients)
        clients = [
            BrowserShieldFlowerClient(cid, partitions[cid][0], partitions[cid][1], enable_dp=enable_dp)
            for cid in range(num_clients)
        ]

        # Initial global parameters from client 0
        global_params = clients[0].get_parameters({})
        
        history_rounds = []

        for round_idx in range(1, num_rounds + 1):
            client_updates = []
            round_accs = []
            round_losses = []

            for client in clients:
                fit_params, num_samples, metrics = client.fit(global_params, {})
                loss, _, eval_metrics = client.evaluate(fit_params, {})
                client_updates.append((fit_params, num_samples))
                round_accs.append(eval_metrics["accuracy"])
                round_losses.append(loss)

            # Aggregate using FedAvg or FedProx
            if strategy_name == "FedProx":
                global_params = FedProxStrategy.aggregate(client_updates)
            else:
                global_params = FedAvgStrategy.aggregate(client_updates)

            avg_acc = float(np.mean(round_accs))
            avg_loss = float(np.mean(round_losses))

            history_rounds.append({
                "round": round_idx,
                "accuracy": round(avg_acc, 4),
                "loss": round(avg_loss, 4),
                "communication_cost_bytes": len(global_params) * 42 * 4 * 2 # Float32 params transmitted up/down
            })

        return {
            "strategy": strategy_name,
            "num_clients": num_clients,
            "num_rounds": num_rounds,
            "privacy_enabled": enable_dp,
            "final_accuracy": history_rounds[-1]["accuracy"] if history_rounds else 0.0,
            "round_history": history_rounds
        }
