# Model Card — Lightweight Robo-Advisor

## Overview
- Purpose: Offline evaluation of simple allocation strategies (60/40, Risk Parity, TS-Momentum).
- Users: Educational / research, not investment advice.
- Data: Kaggle public datasets (see data/README.md).

## Performance summary (fill after experiments)
- Test window: 
- Metrics: CAGR, Vol, Sharpe, Sortino, MaxDD, Turnover, TE.

## Limitations
- Survivorship bias possible if universe is static.
- Monthly frequency may miss intramonth dynamics.
- Momentum may whipsaw in range-bound markets.

## Governance
- Data refresh cadence: quarterly
- Parameter review: semi-annual
- Change log: docs/changelog.md
