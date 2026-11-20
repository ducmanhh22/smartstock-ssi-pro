import sqlite3
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
DB=Path(__file__).with_name('stock_history.db')

def initialize():
    with sqlite3.connect(DB) as con:
        con.execute('CREATE TABLE IF NOT EXISTS candles (source TEXT NOT NULL, symbol TEXT NOT NULL, candle_time TEXT NOT NULL, open REAL, high REAL, low REAL, close REAL, volume REAL, collected_vn TEXT NOT NULL, PRIMARY KEY(source,symbol,candle_time))')

def save(df,source,symbol):
    initialize()
    timestamp=datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).isoformat()
    with sqlite3.connect(DB) as con:
        con.executemany('INSERT OR IGNORE INTO candles VALUES (?,?,?,?,?,?,?,?,?)',[(source,symbol,str(row.Time),float(row.Open),float(row.High),float(row.Low),float(row.Close),float(row.Volume),timestamp) for row in df.itertuples()])

def load(source,symbol):
    initialize()
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query('SELECT candle_time as Time,open as Open,high as High,low as Low,close as Close,volume as Volume FROM candles WHERE source=? AND symbol=? ORDER BY candle_time',con,params=(source,symbol))
