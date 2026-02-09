# BTC-TRADING CONTEXT (Session Handoff)

Use this as the canonical context if chat history is cleared.

## Project tag
- `[btc-trading]`

## Data locations
- BTC: `/home/ttang/Desktop/trading/bitcoin_daily_usd_stooq.csv`
- ETH:
  - `/home/ttang/Desktop/trading/ethereum_daily_usd_bitstamp.csv`
  - `/home/ttang/Desktop/trading/ethereum_daily_usd_gemini.csv`
  - `/home/ttang/Desktop/trading/ethereum_daily_usd_yahoo.csv`

## Prior BTC strategy summary
- Strategy tested: `vol_mom(lookback=10, vol_lookback=30, vol_thresh=0.1)`
- Cost assumption: `0.10%` per side
- Bias policy: no look-ahead (signals from t-1 info)
- Robust target used: CAGR >= 60%, MaxDD < 25%
- Result: target **not met robustly** (drawdowns too high)

### BTC headline metrics (from prior report)
- IS: CAGR 642.13%, MaxDD 62.70%, Sharpe 2.515
- OOS: CAGR 5.51%, MaxDD 48.64%, Sharpe 0.402
- Full: CAGR 310.62%, MaxDD 62.70%, Sharpe 2.011
- WF OOS agg: CAGR 96.96%, MaxDD 63.46%, Sharpe 1.309

## Working conventions
- If user says “go to btc-trading”, load this file first.
- Treat this file + current CSVs as source of truth for reset sessions.
