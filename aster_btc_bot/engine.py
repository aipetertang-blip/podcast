import json
import os
import time
from datetime import datetime, timezone
from strategy import b_dual_mom_target


class BotEngine:
    def __init__(self, cfg, adapter):
        self.cfg = cfg
        self.adapter = adapter
        self.state_path = cfg['state_path']
        self.state = self._load_state()

    def _load_state(self):
        if os.path.exists(self.state_path):
            with open(self.state_path) as f:
                return json.load(f)
        return {
            'last_decision_day': None,
            'equity_curve': [1.0],
            'daily_returns': [],
            'last_price': None,
            'halted': False,
        }

    def _save_state(self):
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        with open(self.state_path, 'w') as f:
            json.dump(self.state, f, indent=2)

    def _utc_day(self):
        return datetime.now(timezone.utc).strftime('%Y-%m-%d')

    def _after_buffer(self):
        now = datetime.now(timezone.utc)
        mins = self.cfg.get('decision_buffer_minutes', 10)
        return now.hour == 0 and now.minute >= mins or now.hour > 0

    def _mark_to_market(self, price):
        lp = self.state.get('last_price')
        if lp is None:
            self.state['last_price'] = price
            return
        pos = self.adapter.get_position(self.cfg['symbol'])
        ret = pos * ((price / lp) - 1.0)
        self.state['daily_returns'].append(ret)
        eq_prev = self.state['equity_curve'][-1]
        self.state['equity_curve'].append(eq_prev * (1.0 + ret))
        self.state['last_price'] = price

        # simple kill switch on daily loss
        max_loss = self.cfg['risk'].get('max_daily_loss_pct', 0.05)
        if ret <= -abs(max_loss):
            self.state['halted'] = True

    def run_once(self):
        if not self.cfg.get('enabled', True):
            return {'status': 'disabled'}
        if self.state.get('halted'):
            return {'status': 'halted'}

        symbol = self.cfg['symbol']
        price = self.adapter.get_mark_price(symbol)
        self._mark_to_market(price)

        day = self._utc_day()
        if self.state['last_decision_day'] == day:
            self._save_state()
            return {'status': 'already_decided_today'}
        if not self._after_buffer():
            self._save_state()
            return {'status': 'waiting_for_daily_close_buffer'}

        closes = self.adapter.fetch_daily_closes(symbol, 500)
        target_lev = b_dual_mom_target(closes, self.state['equity_curve'], self.cfg['strategy'])

        notional = self.cfg['risk']['notional_usd']
        target_notional = target_lev * notional
        target_btc = target_notional / price if price > 0 else 0.0

        result = self.adapter.set_target_position(symbol, target_btc)
        self.state['last_decision_day'] = day
        self._save_state()

        return {
            'status': 'ok',
            'symbol': symbol,
            'price': price,
            'target_leverage_proxy': target_lev,
            'target_btc': target_btc,
            'order_result': result,
        }

    def run_forever(self):
        poll = int(self.cfg.get('poll_seconds', 60))
        while True:
            out = self.run_once()
            print(json.dumps(out, default=str))
            time.sleep(poll)
