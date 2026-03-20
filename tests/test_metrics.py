import numpy as np
import pandas as pd

from src.metrics.perf import cagr, sharpe, sortino, tracking_error, turnover
from src.metrics.risk import annual_volatility, max_drawdown


def test_max_drawdown_known_case():
    nav = pd.Series([1.0, 1.2, 0.9, 1.1])
    # Peak 1.2 -> trough 0.9 => dd = 0.9/1.2 - 1 = -0.25
    assert abs(max_drawdown(nav) - (-0.25)) < 1e-12


def test_annual_volatility_zero_when_constant_returns():
    rets = pd.Series([0.0] * 24)
    assert annual_volatility(rets, periods_per_year=12) == 0.0


def test_sharpe_nan_when_zero_std():
    rets = pd.Series([0.01] * 12)
    assert np.isnan(sharpe(rets))


def test_tracking_error_zero_when_same_series():
    rets = pd.Series([0.01, -0.02, 0.03])
    assert tracking_error(rets, rets) == 0.0


def test_turnover_simple_case():
    # two months, change from [0.5,0.5] to [0.6,0.4] => abs change sum=0.2
    w = pd.DataFrame([[0.5, 0.5], [0.6, 0.4]], columns=["A", "B"])
    # One-way turnover convention: 0.5 * sum(abs changes)
    # sum(abs changes)=0.2 => one-way monthly=0.1 => annualised=0.1*12=1.2
    assert abs(turnover(w) - 1.2) < 1e-12

