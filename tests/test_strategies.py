import pandas as pd
import numpy as np

from src.strategies.risk_parity import risk_parity_weights
from src.strategies.momentum import ts_momentum_weights


def test_risk_parity_returns_zero_when_insufficient_history():
    idx = pd.to_datetime(["2020-01-31", "2020-02-29"])
    prices = pd.DataFrame({"A": [100, 101], "B": [100, 99]}, index=idx)

    w = risk_parity_weights(prices, window_months=12)
    assert (w == 0).all()
    assert set(w.index) == {"A", "B"}


def test_risk_parity_prefers_lower_vol_asset():
    # Make A low vol, B high vol over the last 12 months
    idx = pd.date_range("2020-01-31", periods=13, freq="M")
    # A: smooth +1% monthly
    A = 100 * (1.01 ** np.arange(len(idx)))
    # B: alternating +5% / -5% (more volatile)
    B = 100 * np.cumprod([1.0] + [1.05 if i % 2 == 0 else 0.95 for i in range(1, len(idx))])

    prices = pd.DataFrame({"A": A, "B": B}, index=idx)
    w = risk_parity_weights(prices, window_months=12)

    assert w["A"] > w["B"]
    assert abs(w.sum() - 1.0) < 1e-9


def test_momentum_all_negative_gives_zero_weights():
    idx = pd.date_range("2020-01-31", periods=13, freq="M")
    # Both assets falling
    prices = pd.DataFrame(
        {"A": np.linspace(100, 80, len(idx)), "B": np.linspace(100, 90, len(idx))},
        index=idx,
    )
    w = ts_momentum_weights(prices, lookback_months=12)
    assert (w == 0).all()


def test_momentum_positive_assets_sum_to_one():
    idx = pd.date_range("2020-01-31", periods=13, freq="M")
    prices = pd.DataFrame(
        {"A": np.linspace(100, 120, len(idx)), "B": np.linspace(100, 110, len(idx))},
        index=idx,
    )
    w = ts_momentum_weights(prices, lookback_months=12)
    assert w.sum() == 1.0
    assert (w >= 0).all()
