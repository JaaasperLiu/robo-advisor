import pandas as pd
from src.run_pipeline import apply_nan_policy_ffill_dropna

def test_ffill_then_dropna_removes_leading_nans_and_fills_gaps():
    idx = pd.to_datetime(["2020-01-31","2020-02-29","2020-03-31"])
    prices = pd.DataFrame(
        {"A":[None, 100.0, None], "B":[None, None, 200.0]},
        index=idx
    )

    out = apply_nan_policy_ffill_dropna(prices)

    # Leading NaNs should be dropped (no row where B is NaN remains)
    assert out.index.min() == pd.to_datetime("2020-03-31")

    # A should forward-fill across its gap before dropna
    assert out.loc[pd.to_datetime("2020-03-31"), "A"] == 100.0
    assert out.loc[pd.to_datetime("2020-03-31"), "B"] == 200.0

def test_non_numeric_values_are_coerced_then_handled():
    idx = pd.to_datetime(["2020-01-31","2020-02-29","2020-03-31"])
    prices = pd.DataFrame({"A":["bad", "100", "101"], "B":[200, 201, 202]}, index=idx)

    out = apply_nan_policy_ffill_dropna(prices)

    # First row becomes NaN for A and then gets dropped
    assert len(out) == 2
    assert out["A"].dtype.kind in ("f","i")
