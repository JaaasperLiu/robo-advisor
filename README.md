# A Reproducible Algorithmic Backtesting System

This repository contains the source code for a modular, offline backtesting system designed to evaluate algorithmic portfolio strategies with a strong focus on correctness, reproducibility, and engineering robustness. The system is the subject of the dissertation, "Design and Evaluation of a Reproducible Algorithmic Backtesting System."

It provides a complete, end-to-end pipeline for ingesting price data, computing features, simulating portfolio performance with a walk-forward methodology, and generating a rich set of auditable output artefacts. The project uses two transparent, rule-based strategies as case studies: an inverse-volatility approximation of **Risk Parity** and a **Time-Series Momentum** strategy.

## Core Engineering Features

- **Modular Architecture**: The system is organized into distinct, testable stages for data ingestion, feature generation, strategy logic, portfolio simulation, and evaluation.
- **Deterministic Execution**: Given the same inputs and configuration, the pipeline is guaranteed to produce identical outputs. This is verified via a hash-based protocol.
- **Automated Testing**: A suite of 14 unit tests (`pytest`) validates the correctness of the core backtesting engine, metrics calculations, and data handling policies.
- **Robustness and Failure Handling**: The system includes explicit, logged policies for handling common data issues like missing values and duplicate timestamps.
- **Auditable Artefacts**: For each run, the pipeline exports a complete set of results, including equity curves, monthly weights, performance metrics, and the exact configuration used.

## Project Structure

```
robo-advisor-offline/
|-- config/                 # YAML files for backtest parameters & asset universe
|-- data/                   # Input price data (e.g., prices_monthly.csv)
|-- docs/                   # Documentation templates (e.g., model card)
|-- notebooks/              # Jupyter notebooks for analysis and visualization
|-- reports/                # All output artefacts (metrics, weights, logs, hashes)
|-- src/                    # Main source code for the backtesting pipeline
|   |-- backtest/           # Core portfolio simulation engine
|   |-- metrics/            # Performance and risk calculation functions
|   |-- strategies/         # Strategy logic (risk_parity.py, momentum.py)
|   |-- utils/              # Helper functions
|   `-- run_pipeline.py     # Main entry point to run the backtests
|-- tests/                  # Pytest suite for unit and integration tests
|-- requirements.txt        # Python package dependencies
`-- README.md               # This file
```

## Setup and Usage

### 1. Prerequisites

- Python 3.10+
- An environment with the packages listed in `requirements.txt` installed.

### 2. Installation

Clone the repository and install the required packages:

```bash
git clone <repository_url>
cd robo-advisor-offline
pip install -r requirements.txt
```

### 3. Running the Pipeline

To run the full backtesting pipeline for both strategies, execute the main script from the root directory:

```bash
python3 src/run_pipeline.py
```

Upon completion, all output artefacts—including metrics, equity curves, weights, logs, and reproducibility hashes—will be saved to the `reports/` directory.

### 4. Running the Tests

To verify the correctness of the core components, run the automated test suite:

```bash
pytest
```

### 5. Exploratory Analysis

The `notebooks/` directory contains Jupyter notebooks for deeper analysis, visualization, and replication of the figures and tables presented in the dissertation.

## Disclaimer

This project is for educational and research purposes only. The strategies, data, and results are part of a controlled academic study and do not constitute investment advice. The system is not intended for live trading.
