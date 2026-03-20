import numpy as np
import pandas as pd

def cagr(nav: pd.Series, periods_per_year: int = 12):
    if len(nav) < 2:
        return np.nan
    total = nav.iloc[-1] / nav.iloc[0]
    years = len(nav) / periods_per_year
    return total ** (1/years) - 1

def sharpe(returns: pd.Series, rf: float = 0.0, periods_per_year: int = 12):
    ex = returns - rf/periods_per_year
    denom = ex.std()
    if denom == 0 or np.isclose(denom, 0.0):
        return np.nan
    return np.sqrt(periods_per_year) * ex.mean() / denom

def sortino(returns: pd.Series, rf: float = 0.0, periods_per_year: int = 12):
    downside = returns[returns < 0]
    denom = downside.std()
    if denom == 0 or np.isnan(denom):
        return np.nan
    ex = returns - rf/periods_per_year
    return np.sqrt(periods_per_year) * ex.mean() / denom

def tracking_error(returns: pd.Series, benchmark: pd.Series):
    r, b = returns.align(benchmark, join='inner')
    diff = r - b
    return diff.std() * np.sqrt(12)

def turnover(weights: pd.DataFrame):
    # Annualized turnover given monthly weights (sum abs changes)
    if weights.shape[0] < 2:
        return np.nan
    monthly = weights.diff().abs().sum(axis=1).mean()
    return monthly * 12
