import numpy as np
import pandas as pd

def annual_volatility(returns: pd.Series, periods_per_year: int = 12):
    return returns.std() * np.sqrt(periods_per_year)

def max_drawdown(nav: pd.Series):
    cummax = nav.cummax()
    dd = nav / cummax - 1.0
    return dd.min()
