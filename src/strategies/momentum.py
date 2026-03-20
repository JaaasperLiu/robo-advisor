import pandas as pd
import numpy as np

def ts_momentum_weights(prices: pd.DataFrame, lookback_months: int = 12, top_k: int = None):
    rets = prices.pct_change().dropna()
    if len(rets) < lookback_months:
        return pd.Series(0, index=prices.columns)
    mom = (prices / prices.shift(lookback_months) - 1).iloc[-1]
    pos = (mom > 0).astype(float)
    if top_k is not None and pos.sum() > top_k:
        top = mom.sort_values(ascending=False).head(top_k).index
        w = pd.Series(0, index=prices.columns)
        w[top] = 1.0 / top_k
        return w
    if pos.sum() == 0:
        return pd.Series(0, index=prices.columns)
    return pos / pos.sum()
