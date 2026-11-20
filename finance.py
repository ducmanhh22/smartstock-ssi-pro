"""Descriptive technical indicators for OHLCV. No trade recommendations."""
import numpy as np
import pandas as pd

COLUMNS = ('Time', 'Open', 'High', 'Low', 'Close', 'Volume')


def analyze(frame: pd.DataFrame) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame(columns=[*COLUMNS, 'SMA5', 'SMA20', 'EMA12', 'RSI14', 'MACD', 'MACDSignal', 'BBUpper', 'BBLower', 'VolMA20', 'RangePct', 'ReturnPct'])
    df = frame.copy()
    for key in COLUMNS:
        if key not in df:
            raise ValueError(f'Thiếu cột dữ liệu: {key}')
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    for key in COLUMNS[1:]:
        df[key] = pd.to_numeric(df[key], errors='coerce')
    df = df.dropna(subset=list(COLUMNS))
    df = df[(df[['Open','High','Low','Close']] > 0).all(axis=1) & (df['Volume'] >= 0)]
    df = df[(df['High'] >= df[['Open','Close','Low']].max(axis=1)) & (df['Low'] <= df[['Open','Close','High']].min(axis=1))]
    df = df.drop_duplicates(subset=['Time'], keep='last').sort_values('Time').reset_index(drop=True)
    if df.empty:
        return analyze(pd.DataFrame(columns=COLUMNS))
    close = df['Close']
    df['ReturnPct'] = close.pct_change() * 100
    df['RangePct'] = (df['High'] - df['Low']) / df['Open'] * 100
    df['SMA5'] = close.rolling(5, min_periods=5).mean()
    df['SMA20'] = close.rolling(20, min_periods=20).mean()
    df['EMA12'] = close.ewm(span=12, adjust=False).mean()
    df['VolMA20'] = df['Volume'].rolling(20, min_periods=20).mean()
    std20 = close.rolling(20, min_periods=20).std(ddof=0)
    df['BBUpper'] = df['SMA20'] + 2 * std20
    df['BBLower'] = df['SMA20'] - 2 * std20
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14, min_periods=14).mean()
    loss = (-delta.clip(upper=0)).rolling(14, min_periods=14).mean()
    ratio = gain / loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + ratio)
    rsi = rsi.mask((loss == 0) & (gain > 0), 100.0)
    rsi = rsi.mask((loss == 0) & (gain == 0), 50.0)
    df['RSI14'] = rsi
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    df['MACD'] = ema12 - ema26
    df['MACDSignal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df


def summarize(df: pd.DataFrame):
    if df.empty:
        return None
    first, last = df.iloc[0], df.iloc[-1]
    return {
        'last_close': float(last['Close']),
        'window_change_pct': float((last['Close'] / first['Open'] - 1) * 100),
        'total_volume': float(df['Volume'].sum()),
        'candles': len(df),
        'last_time': pd.Timestamp(last['Time']).strftime('%d/%m/%Y %H:%M'),
        'window_high': float(df['High'].max()),
        'window_low': float(df['Low'].min()),
        'window_open': float(first['Open']),
    }


def describe(df: pd.DataFrame) -> str:
    if df.empty or len(df) < 20:
        return 'Chưa đủ 20 nến hợp lệ để đánh giá vị trí giá so với SMA20.'
    latest = df.iloc[-1]
    if latest['Close'] > latest['SMA20']:
        return 'Giá đóng nến hiện nằm trên SMA20. Đây là mô tả xu hướng trên mẫu dữ liệu đang xem, không phải khuyến nghị mua.'
    if latest['Close'] < latest['SMA20']:
        return 'Giá đóng nến hiện nằm dưới SMA20. Đây là mô tả xu hướng trên mẫu dữ liệu đang xem, không phải khuyến nghị bán.'
    return 'Giá đóng nến đang trùng với đường SMA20.'
