"""
src/run_pipeline.py

Deterministic end-to-end pipeline.

From repo root:
    python3 -m src.run_pipeline --strategy=risk_parity
    python3 -m src.run_pipeline --strategy=momentum

Optional:
    python3 -m src.run_pipeline --strategy=risk_parity --start 2006-01-31 --end 2021-12-31
    python3 -m src.run_pipeline --strategy=risk_parity --tc_bps 5 --max_weight 0.25
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
REPORTS_DIR = REPO_ROOT / "reports"


# -------------------------
# Config
# -------------------------
@dataclass(frozen=True)
class PipelineConfig:
    strategy: str
    seed: int
    transaction_cost_bps: float
    max_weight: float
    prices_csv: str
    start: Optional[str] = None
    end: Optional[str] = None


# -------------------------
# CLI
# -------------------------
def parse_args() -> PipelineConfig:
    p = argparse.ArgumentParser(description="Run the backtesting pipeline end-to-end.")
    p.add_argument(
        "--strategy",
        required=True,
        choices=["risk_parity", "momentum"],
        help="Strategy to run",
    )
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--tc_bps", type=float, default=10.0, help="Transaction cost in bps")
    p.add_argument("--max_weight", type=float, default=0.35, help="Per-asset max weight cap")
    p.add_argument(
        "--prices_csv",
        type=str,
        default=str(DATA_DIR / "prices_monthly.csv"),
        help="Wide monthly prices CSV (index=dates, columns=tickers)",
    )
    p.add_argument("--start", type=str, default=None, help="Optional start date YYYY-MM-DD")
    p.add_argument("--end", type=str, default=None, help="Optional end date YYYY-MM-DD")

    a = p.parse_args()
    return PipelineConfig(
        strategy=a.strategy,
        seed=a.seed,
        transaction_cost_bps=a.tc_bps,
        max_weight=a.max_weight,
        prices_csv=a.prices_csv,
        start=a.start,
        end=a.end,
    )


# -------------------------
# Determinism
# -------------------------
def set_determinism(seed: int) -> None:
    """
    Uses src/utils/seed.py if present; otherwise falls back to numpy.
    """
    try:
        from src.utils.seed import set_seed  # type: ignore

        set_seed(seed)
    except Exception:
        np.random.seed(seed)


# -------------------------
# Writers
# -------------------------
def write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)


def write_df(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=True)


# -------------------------
# Data
# -------------------------
def apply_nan_policy_ffill_dropna(prices: pd.DataFrame) -> pd.DataFrame:
    """
    NaN policy:
    1) forward-fill missing prices
    2) drop rows that still contain NaNs (typically leading history)
    """
    if prices.empty:
        return prices

    prices = prices.apply(pd.to_numeric, errors="coerce")
    prices = prices.ffill()
    prices = prices.dropna(axis=0, how="any")
    return prices

def load_prices(cfg: PipelineConfig) -> pd.DataFrame:
    path = Path(cfg.prices_csv)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"Prices CSV not found: {path}\n"
            f"Provide --prices_csv or create data/prices_monthly.csv"
        )

    prices = pd.read_csv(path, index_col=0, parse_dates=True)

    # Deterministic ordering
    prices = prices.sort_index()
    prices = prices.sort_index(axis=1)

    # Optional filters
    if cfg.start:
        prices = prices.loc[prices.index >= pd.to_datetime(cfg.start)]
    if cfg.end:
        prices = prices.loc[prices.index <= pd.to_datetime(cfg.end)]

    # Duplicate date policy: deterministic
    if not prices.index.is_unique:
        n_dupes = prices.index.duplicated(keep="last").sum()
        prices = prices[~prices.index.duplicated(keep="last")]
        print(f"[DataClean] Dropped {n_dupes} duplicate date rows (kept last).")

    before_shape = prices.shape
    prices = apply_nan_policy_ffill_dropna(prices)
    after_shape = prices.shape

    if after_shape != before_shape:
        print(f"[DataClean] NaN policy ffill+dropna: {before_shape} -> {after_shape}")
        
    if prices.shape[0] < 2:
        raise ValueError("Need at least 2 rows of prices to compute returns.")
    if prices.shape[1] < 1:
        raise ValueError("Need at least 1 asset column in prices.")

    return prices


# -------------------------
# Strategy loader
# -------------------------
def load_strategy(strategy: str) -> Callable[[pd.DataFrame], pd.Series]:
    """
    Matches your actual function names in src/strategies.
    """
    if strategy == "risk_parity":
        from src.strategies.risk_parity import risk_parity_weights  # type: ignore

        return risk_parity_weights

    if strategy == "momentum":
        from src.strategies.momentum import ts_momentum_weights  # type: ignore

        return ts_momentum_weights

    raise ValueError(f"Unknown strategy: {strategy}")


# -------------------------
# Backtest
# -------------------------
def run_backtest(
    prices: pd.DataFrame,
    weight_func: Callable[[pd.DataFrame], pd.Series],
    cfg: PipelineConfig,
) -> Tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
    """
    Calls your engine:
        monthly_rebalance(prices, weight_func, max_weight, cost_bps)
    Returns:
        nav (Series), weights (DataFrame), returns (DataFrame of asset returns)
    """
    from src.backtest.core import monthly_rebalance  # type: ignore

    nav, weights, returns = monthly_rebalance(
        prices=prices,
        weight_func=weight_func,
        max_weight=cfg.max_weight,
        cost_bps=cfg.transaction_cost_bps,
    )
    return nav, weights, returns


# -------------------------
# Metrics
# -------------------------
def choose_benchmark(asset_returns: pd.DataFrame) -> pd.Series:
    """
    Prefer SPY if present; otherwise equal-weight benchmark.
    """
    if "SPY" in asset_returns.columns:
        return asset_returns["SPY"]
    return asset_returns.mean(axis=1)


def compute_metrics(
    nav: pd.Series,
    weights: pd.DataFrame,
    asset_returns: pd.DataFrame,
) -> Dict[str, float]:
    """
    Uses functions already defined in src/metrics.
    """
    from src.metrics import (  # type: ignore
        annual_volatility,
        cagr,
        max_drawdown,
        sharpe,
        sortino,
        tracking_error,
        turnover,
    )

    nav = nav.astype(float)
    port_r = nav.pct_change().dropna()

    bench = choose_benchmark(asset_returns).dropna()
    r_aligned, b_aligned = port_r.align(bench, join="inner")

    out: Dict[str, float] = {
        "n_periods": float(len(port_r)),
        "cagr": float(cagr(nav)),
        "ann_vol": float(annual_volatility(r_aligned)) if len(r_aligned) > 1 else float("nan"),
        "sharpe": float(sharpe(r_aligned)) if len(r_aligned) > 1 else float("nan"),
        "sortino": float(sortino(r_aligned)) if len(r_aligned) > 1 else float("nan"),
        "max_drawdown": float(max_drawdown(nav)),
        "turnover": float(turnover(weights)) if weights.shape[0] > 1 else float("nan"),
        "tracking_error": float(tracking_error(r_aligned, b_aligned)) if len(r_aligned) > 1 else float("nan"),
    }
    return out


# -------------------------
# Main
# -------------------------
def main() -> None:
    cfg = parse_args()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    set_determinism(cfg.seed)

    # Save config (reproducibility evidence)
    write_json(
        REPORTS_DIR / "last_run_config.json",
        {"config": asdict(cfg), "repo_root": str(REPO_ROOT)},
    )

    prices = load_prices(cfg)
    weight_func = load_strategy(cfg.strategy)

    nav, weights, asset_returns = run_backtest(prices, weight_func, cfg)

    # Standardised outputs
    equity_df = nav.astype(float).to_frame(name="equity")
    metrics_df = pd.DataFrame([compute_metrics(nav, weights, asset_returns)])

    write_df(REPORTS_DIR / f"equity_curve_{cfg.strategy}.csv", equity_df)
    write_df(REPORTS_DIR / f"weights_{cfg.strategy}.csv", weights)
    write_df(REPORTS_DIR / f"returns_{cfg.strategy}.csv", asset_returns)
    write_df(REPORTS_DIR / f"metrics_{cfg.strategy}.csv", metrics_df)

    # Debug JSON WITHOUT Timestamp keys (records format)
    equity_head = equity_df.head(5).reset_index().rename(columns={"index": "date"})
    equity_tail = equity_df.tail(5).reset_index().rename(columns={"index": "date"})

    write_json(
        REPORTS_DIR / "last_run_results_raw.json",
        {
            "equity_head": equity_head.to_dict(orient="records"),
            "equity_tail": equity_tail.to_dict(orient="records"),
            "weights_shape": list(weights.shape),
            "returns_shape": list(asset_returns.shape),
            "tickers": list(asset_returns.columns),
        },
    )

    print(f"[OK] Pipeline finished. Outputs written to: {REPORTS_DIR}")
    print(f" - last_run_config.json")
    print(f" - equity_curve_{cfg.strategy}.csv")
    print(f" - weights_{cfg.strategy}.csv")
    print(f" - returns_{cfg.strategy}.csv")
    print(f" - metrics_{cfg.strategy}.csv")
    print(f" - last_run_results_raw.json")


if __name__ == "__main__":
    main()
