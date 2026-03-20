import pandas as pd
import numpy as np

def monthly_rebalance(prices: pd.DataFrame, weight_func, max_weight=0.35, cost_bps=10):
    '''
    prices: wide DataFrame (month-end), columns=tickers, values=adj close
    weight_func: callable(prices_hist) -> pd.Series of weights
    '''
    returns = prices.pct_change().fillna(0.0)
    dates = prices.index
    weights = pd.DataFrame(index=dates, columns=prices.columns, data=0.0)
    nav = pd.Series(index=dates, dtype=float)
    nav.iloc[0] = 1.0
    prev_w = pd.Series(index=prices.columns, data=0.0)

    for i in range(1, len(dates)):
        window = prices.iloc[:i]
        w = weight_func(window).reindex(prices.columns).fillna(0.0)
        w = w.clip(lower=0, upper=max_weight)
        if w.sum() > 1.0:
            w = w / w.sum()
        tc = (w - prev_w).abs().sum() * (cost_bps/10000.0)
        r = (returns.iloc[i] * prev_w).sum() - tc
        nav.iloc[i] = nav.iloc[i-1] * (1 + r)
        prev_w = w
        weights.iloc[i] = prev_w.values
    return nav, weights, returns
