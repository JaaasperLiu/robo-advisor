# Data

This directory is excluded from version control. You need to provide your own price data to run the pipeline.

## Expected File

**`prices_monthly.csv`** — Monthly adjusted close prices in wide format.

### Format

| date       | DIA    | EEM    | EFA    | IEF    | IWM    | QQQ    | SHY    | SPY    |
|------------|--------|--------|--------|--------|--------|--------|--------|--------|
| 2003-02-28 | 79.21  | 12.55  | 18.30  | 83.46  | 68.57  | 23.88  | 80.48  | 83.72  |
| 2003-03-31 | 78.29  | 12.32  | 17.97  | 84.07  | 67.11  | 23.73  | 80.52  | 82.91  |
| ...        | ...    | ...    | ...    | ...    | ...    | ...    | ...    | ...    |

- **Index column**: End-of-month dates (`YYYY-MM-DD`)
- **Columns**: One per ETF ticker
- **Values**: Adjusted close prices (USD)

## Asset Universe

| Ticker | Description            |
|--------|------------------------|
| SPY    | S&P 500                |
| QQQ    | Nasdaq 100             |
| IWM    | Russell 2000           |
| EFA    | International Developed |
| EEM    | Emerging Markets       |
| IEF    | 7-10 Year Treasuries   |
| SHY    | 1-3 Year Treasuries    |
| DIA    | Dow Jones Industrial   |

## How to Obtain the Data

Run notebook `notebooks/01_data_prep.ipynb`, which downloads monthly prices via `yfinance` and saves them to this directory.
