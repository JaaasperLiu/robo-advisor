import pandas as pd
import numpy as np

def risk_parity_weights(prices: pd.DataFrame, window_months: int = 12):
    # Inverse-volatility approximation
    rets = prices.pct_change().dropna()
    if len(rets) < window_months:
        return pd.Series(0, index=prices.columns)
    vol = rets.tail(window_months).std().replace(0, np.nan)
    inv = 1.0 / vol
    w = inv / inv.sum()
    return w.fillna(0.0)
