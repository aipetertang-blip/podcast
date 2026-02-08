import math


def sma(values, n):
    if len(values) < n:
        return None
    return sum(values[-n:]) / n


def realized_vol_annual(daily_rets, lookback):
    if len(daily_rets) < lookback:
        return None
    w = daily_rets[-lookback:]
    rv_d = math.sqrt(sum(x * x for x in w) / len(w))
    return rv_d * math.sqrt(365.0)


def max_drawdown(equity_curve):
    peak = equity_curve[0]
    mdd = 0.0
    for x in equity_curve:
        if x > peak:
            peak = x
        dd = 1.0 - x / peak if peak > 0 else 0.0
        mdd = max(mdd, dd)
    return mdd


def b_dual_mom_target(closes, equity_curve, cfg):
    """
    Return target exposure in [-maxlev, maxlev].
    No-lookahead usage is enforced by caller: closes must be completed daily bars only.
    """
    ms = cfg["ms"]
    ml = cfg["ml"]
    tr = cfg["tr"]
    v = cfg["v"]
    tv = cfg["tv"]
    dd1 = cfg["dd1"]
    dd2 = cfg["dd2"]
    maxlev = cfg["maxlev"]

    need = max(ms, ml, tr, v) + 2
    if len(closes) < need:
        return 0.0

    # dual momentum consensus
    mom_s = closes[-1] / closes[-1 - ms] - 1.0
    mom_l = closes[-1] / closes[-1 - ml] - 1.0
    if mom_s > 0 and mom_l > 0:
        base = 1.0
    elif mom_s < 0 and mom_l < 0:
        base = -1.0
    else:
        base = 0.0

    # trend-aware risk dampening using long SMA approximation
    tr_ma = sma(closes, tr)
    if tr_ma is not None:
        bull = closes[-1] >= tr_ma
        if bull and base < 0:
            base *= 0.5
        if (not bull) and base > 0:
            base *= 0.75

    # vol targeting
    rets = [0.0]
    for i in range(1, len(closes)):
        rets.append(closes[i] / closes[i - 1] - 1.0)
    rv_a = realized_vol_annual(rets[1:], v)
    if rv_a is None or rv_a <= 1e-9:
        lev = 0.0
    else:
        lev = min(maxlev, max(0.0, tv / rv_a))

    target = base * lev

    # drawdown overlays from strategy equity
    if equity_curve:
        mdd = max_drawdown(equity_curve)
        if mdd >= dd2:
            target *= 0.0
        elif mdd >= dd1:
            target *= 0.5

    # cap
    target = max(-maxlev, min(maxlev, target))
    return target
