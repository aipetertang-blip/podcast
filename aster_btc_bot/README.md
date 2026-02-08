# Aster BTCUSDT Perp Bot (scaffold, ready for API wiring)

This bot implements the **B_dual_mom** strategy selected from your robustness research, with:
- no-lookahead signal timing (uses completed daily candles only)
- volatility targeting + conservative leverage cap
- drawdown overlays
- daily execution cycle for BTCUSDT perpetual
- paper mode by default

## Strategy (B_dual_mom)
Parameters (from robust report):
- `ms=10` (short momentum lookback)
- `ml=120` (long momentum lookback)
- `tr=150` (trend filter lookback)
- `v=20` (realized vol lookback)
- `tv=0.25` (target annual vol)
- `dd1=0.15`, `dd2=0.25` (drawdown risk overlays)
- `maxlev=0.8` (position cap)

## Files
- `main.py` — runner
- `engine.py` — trading loop + risk controls + order intent
- `strategy.py` — B_dual_mom signal logic
- `adapters/base.py` — exchange adapter interface
- `adapters/aster_placeholder.py` — paper adapter + Aster API TODO stubs
- `config.example.json` — bot config template

## Quick start (paper mode)
```bash
cd /home/ttang/.openclaw/workspace/aster_btc_bot
cp config.example.json config.json
python3 main.py --config config.json
```

## Live wiring (when API details are provided)
Implement these in `adapters/aster_placeholder.py`:
- `fetch_daily_closes()`
- `get_mark_price()`
- `get_position()`
- `set_target_position()`

Then set in `config.json`:
- `mode: "live"`
- API auth fields for Aster

## Safety defaults
- paper mode default
- only `BTCUSDT` allowed
- one decision per completed daily candle
- kill switch via config (`enabled=false`)
