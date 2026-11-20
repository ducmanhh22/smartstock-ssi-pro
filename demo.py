"""Clearly labeled, deterministic SYNTHETIC candles for UI testing only."""
from datetime import datetime, timedelta
import math
import pandas as pd

BASE = {'FPT': 96500, 'HPG': 26600, 'VNM': 64200, 'VCB': 91500,
        'SSI': 29700, 'MWG': 56200, 'VPB': 29300, 'TCB': 35100}


def example_candles(symbol='FPT') -> pd.DataFrame:
    start = datetime(2026, 11, 12, 9, 0)
    seed = sum(ord(ch) for ch in symbol) % 43
    price = float(BASE.get(symbol, 40000))
    rows = []
    for i in range(150):
        minute = 5 * (i % 50)
        session = i // 50
        t = start + timedelta(days=session, minutes=minute)
        # No dependence on random state, so screenshots/tests are reproducible.
        drift = (0.00035 + 0.00007 * math.sin(seed / 9)) * i
        swing = 0.008 * math.sin((i + seed) / 10) + 0.0025 * math.cos((i + seed) / 3.7)
        mid = price * (1 + drift + swing)
        o = round(mid * (1 + 0.0009 * math.sin(i + seed)), 2)
        c = round(mid * (1 + 0.0009 * math.cos(i / 1.8 + seed)), 2)
        h = round(max(o, c) * (1 + .0009 + .0004 * (i % 3)), 2)
        l = round(min(o, c) * (1 - .0009 - .0003 * (i % 4)), 2)
        volume = 4000 + (i % 17) * 310 + int(abs(math.sin(i / 3 + seed)) * 8200)
        rows.append({'Time': t, 'Open': o, 'High': h, 'Low': l,
                     'Close': c, 'Volume': volume})
    return pd.DataFrame(rows)
