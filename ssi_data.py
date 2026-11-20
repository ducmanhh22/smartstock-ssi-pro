"""Read-only SSI FastConnect market data adapter. No trading operations."""
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def fetch_ssi(symbol):
    from ssi_sdk import Auth, Data, Config
    cid=os.getenv('SSI_CLIENT_ID','').strip()
    key=os.getenv('SSI_API_KEY','').strip()
    secret=os.getenv('SSI_API_SECRET','').strip()
    if not all([cid,key,secret]):
        raise ValueError('Thiếu SSI_CLIENT_ID, SSI_API_KEY hoặc SSI_API_SECRET trong .env')
    cfg=Config(client_id=cid,api_key=key,api_secret=secret)
    rows=[]
    with Auth(cfg) as auth:
        auth.authenticate()
        with Data(auth) as data:
            candles=data.market_data.get_ohlc_1minute(symbol)
            for c in candles or []:
                rows.append({'Time':getattr(c,'trading_date',None),'Open':getattr(c,'open_price',None),'High':getattr(c,'high_price',None),'Low':getattr(c,'low_price',None),'Close':getattr(c,'close_price',None),'Volume':getattr(c,'volume',None)})
    if not rows:
        return pd.DataFrame(columns=['Time','Open','High','Low','Close','Volume'])
    return pd.DataFrame(rows)
