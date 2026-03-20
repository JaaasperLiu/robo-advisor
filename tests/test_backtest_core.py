import numpy as np
import pandas as pd

from src.backtest.core import monthly_rebalance


def _make_prices():
    # 4 month-ends, 2 assets, simple deterministic prices
    idx = pd.to_datetime(["2020-01-31", "2020-02-29", "2020-03-31", "2020-04-30"])
    return pd.DataFrame(
        {
            "A": [100.0, 110.0, 121.0, 133.1],  # +10% each month
            "B": [100.0, 100.0, 100.0, 100.0],  # flat
        },
        index=idx,
    )


def test_returns_first_row_is_zero():
    prices = _make_prices()

    def wfunc(_window):
        # Any weights are fine; we are testing returns pre-processing
        return pd.Series({"A": 0.5, "B": 0.5})

    nav, weights, returns = monthly_rebalance(prices, wfunc, max_weight=0.35, cost_bps=10)

    # core.py does: prices.pct_change().fillna(0.0)
    assert (returns.iloc[0] == 0.0).all()


def test_weight_constraints_clip_and_sum_to_one_when_positive():
    prices = _make_prices()

    def wfunc(_window):
        # Intentionally violate constraints: too large and sums > 1
        return pd.Series({"A": 0.9, "B": 0.9})

    nav, weights, returns = monthly_rebalance(prices, wfunc, max_weight=0.35, cost_bps=0)

    # After warmup, weights should respect cap and sum<=1 (your code normalises if sum>1)
    # We check a late row where weights are applied (i >= 1)
    w = weights.iloc[-1]
    assert (w <= 0.35 + 1e-12).all()
    assert w.sum() <= 1.0 + 1e-12
    # Cash is allowed. With 2 assets and max_weight=0.35, the maximum invested is 0.70.
    # Your engine only renormalises when sum > 1, so here it should stay at 0.70.
    if w.sum() > 0:
        assert abs(w.sum() - 0.70) < 1e-9


def test_transaction_cost_applied_on_first_rebalance():
    prices = _make_prices()

    def wfunc(_window):
        # Go fully into A (will be clipped to max_weight then normalised if needed)
        return pd.Series({"A": 1.0, "B": 0.0})

    # Use a large tc so the effect is obvious
    nav, weights, returns = monthly_rebalance(prices, wfunc, max_weight=1.0, cost_bps=100)  # 1%

    # In your engine, at i=1:
    # prev_w starts 0 -> tc = |w-0| sum * 0.01 = 1*0.01 = 0.01
    # r = (returns[i] * prev_w).sum - tc = 0 - 0.01
    # nav[1] = 1 * (1 - 0.01) = 0.99
    assert abs(nav.iloc[1] - 0.99) < 1e-12
