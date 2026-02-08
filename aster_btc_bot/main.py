#!/usr/bin/env python3
import argparse
import json
from adapters.aster_placeholder import AsterPlaceholderAdapter
from engine import BotEngine


def load_config(path):
    with open(path) as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', required=True)
    ap.add_argument('--once', action='store_true', help='Run one cycle and exit')
    args = ap.parse_args()

    cfg = load_config(args.config)

    if cfg.get('symbol') != 'BTCUSDT':
        raise ValueError('This bot is restricted to BTCUSDT only by design.')

    adapter = AsterPlaceholderAdapter(cfg)
    eng = BotEngine(cfg, adapter)

    if args.once:
        print(json.dumps(eng.run_once(), indent=2, default=str))
    else:
        eng.run_forever()


if __name__ == '__main__':
    main()
