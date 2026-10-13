# BrowserShield-X

**Title**: BrowserShield-X: An Explainable Multi-Layer Adaptive File Spoofing Detection and Privacy-Preserving Federated Learning System

BrowserShield-X is an advanced cybersecurity platform and machine learning framework designed to detect file-type spoofing (where a file's declared extension does not match its true binary structure or content). Moving beyond simple magic-byte matching, BrowserShield-X implements a **7-Layer Content Verification Engine**, **Adversarial Spoof Detection**, **Explainable AI (SHAP & feature attribution)**, **Dynamic 0–100 Risk Scoring**, **Archive-Aware Deep Inspection**, **Point-of-Download Monitoring**, **Quarantine Isolation**, **Federated Learning (FedAvg vs. FedProx under Non-IID distributions)**, **Differential Privacy Protection**, **Continual Learning**, and a **10-Page Cybersecurity Web Dashboard**.

---

## 🏗️ System Architecture

```
+-----------------------------------------------------------------------------------+
|                                BROWSER SHIELD-X                                   |
+-----------------------------------------------------------------------------------+
                                          |
                +-------------------------+-------------------------+
                |                                                   |
     [ Point-of-Download Watcher ]                        [ Manual Web Upload ]
                |                                                   |
                +-------------------------+-------------------------+
                                          |
                                          v
                +---------------------------------------------------+
                |            7-LAYER SCANNER ENGINE                 |
                |  Layer 1: Extension Normalization                 |
                |  Layer 2: Magic-Byte / Header Analysis            |
                |  Layer 3: Format-Aware Footer Verification        |
                |  Layer 4: MIME Content Type Discrepancy Check     |
                |  Layer 5: Shannon & Block Entropy Analysis        |
                |  Layer 6: Byte Frequency Distribution & Chi-Sq    |
                |  Layer 7: Structural Parser (PDF, ZIP, PE, Image) |
                +---------------------------------------------------+
                                          |
                +-------------------------+-------------------------+
                |                                                   |
                v                                                   v
  [ 42-Dim Feature Extraction ]                           [ Deterministic Rules ]
                |                                                   |
                v                                                   v
  [ ML Classifier Suite ]                                  [ Anomaly Flags ]
  (LR / RF / XGB / PyTorch NN)                                      |
                |                                                   |
                +-------------------------+-------------------------+
                                          |
                                          v
                +---------------------------------------------------+
                |        RISK ENGINE & EXPLAINABILITY (XAI)         |
                |  - Multi-Factor Risk Score (0 - 100)              |
                |  - Decision: ALLOW / REVIEW / BLOCK               |
                |  - Human-Readable Reasons & SHAP Attribution      |
                +---------------------------------------------------+
                                          |
                 +------------------------+------------------------+
                 |                                                 |
                 v                                                 v
       [ Quarantine Manager ]                             [ Web Dashboard ]
       (Isolate, Hash & Audit Log)                        (10 Active Pages)
                 |                                                 |
                 +------------------------+------------------------+
                                          |
                                          v
                +---------------------------------------------------+
                |     FEDERATED LEARNING & CONTINUAL LEARNING       |
                |  - Flower Framework (FedAvg vs FedProx)           |
                |  - Non-IID Client Data Partitions                 |
                |  - Differential Privacy Noise Injection           |
                |  - Local Elastic Weight Consolidation (EWC)       |
                +---------------------------------------------------+
```

---

## 🔬 Research Contributions & Key Questions

1. **RQ1 (Multi-Layer Efficacy)**: Evaluates whether 7-layer content analysis outperforms traditional single-byte signature detectors.
2. **RQ2 (Adversarial Robustness)**: Tests detection capability when attackers tamper with magic bytes, corrupt footers, or prepend fake headers to PE executables.
3. **RQ3 (Explainability)**: Integrates SHAP value attributions and human-readable audit reasons for automated security blocking.
4. **RQ4 & RQ5 (Federated Learning & Non-IID Drift)**: Evaluates Flower FL simulation comparing **FedAvg** vs. **FedProx** under heterogeneous non-IID client partitions (PDF-heavy, Image/Archive-heavy, Executable-heavy).
5. **RQ6 (Privacy & Communication)**: Implements Gaussian Differential Privacy ($\epsilon=1.5, \delta=10^{-5}$) gradient noise injection while logging communication byte overhead per round.
6. **RQ7 (Continual Learning)**: Prevents catastrophic forgetting via Experience Replay buffer and Elastic Weight Consolidation (EWC).

---

## 💻 10-Page Cybersecurity Web Dashboard

1. **Dashboard**: Live system metrics, risk score trends, threat ticker, and decision donut charts.
2. **Scan File**: Drag-and-drop interactive file scanner with real-time multi-layer audit progress.
3. **Download Monitor**: Real-time status and live feed of point-of-download directory watcher.
4. **Scan History**: Filterable search table of all historic scans, risk scores, and decisions.
5. **Quarantine Vault**: Secure isolation manager supporting file inspection, restore, and permanent delete.
6. **File Security Report**: Comprehensive inspection view featuring Risk Gauge, 7-layer audit checklist, ML probabilities, and SHAP feature importance plot.
7. **Model Analytics**: Centralized ML benchmarks (Logistic Regression, Random Forest, XGBoost, PyTorch MLP) and 7-Step Feature Ablation Study.
8. **Federated Learning**: Flower FL simulation controls, FedAvg vs FedProx convergence graphs, and Non-IID client partition metrics.
9. **Explainability (XAI)**: SHAP feature contribution inspector and synthetic adversarial attack matrix.
10. **System Settings**: Configurable dynamic risk score weights (`rule_engine`, `ml_prediction`, `structural_anomaly`, `mime_mismatch`).

---

## 🚀 Running the System

### 1. Start FastAPI Backend Server
```bash
cd backend
python main.py
```
The backend server runs on `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

### 2. Start React Web Dashboard
```bash
cd frontend
npm run dev
```
Open `http://localhost:5173` in your browser.

### 3. Run PyTest Test Suite & Benchmarks
```bash
python -m pytest tests/
python -c "from experiments.runner import ExperimentRunner; ExperimentRunner.run_all_experiments()"
```
