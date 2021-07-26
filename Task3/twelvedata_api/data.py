import pandas as pd
from twelvedata import TDClient

API_KEY = '228c71b89637460fb89a723c380d16ff'
TICKER = 'AAPL'
TIME_INTERVAL = '1min'

td = TDClient(apikey=API_KEY)

#Change the symbol of the ticker here
ts = td.time_series(
    symbol= TICKER,
    interval= TIME_INTERVAL,
    timezone="America/New_York"
)

data= ts.with_macd().with_macd(fast_period=10).with_stoch().as_pandas()

def get_data():
    return { "datetime": data['datetime'], "macd": data['macd_1'], "macd_signal": data['macd_signal_1'], "macd_hist": data['macd_hist_1'] }