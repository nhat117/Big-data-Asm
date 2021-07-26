import os
import time
from kafka import KafkaProducer
import json
import pandas as pd
import datetime
from twelvedata import TDClient


KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 60))

API_KEY = '228c71b89637460fb89a723c380d16ff'
TICKER = 'AAPL'
INTERVAL = '1min'
INDICATORS = 'macd'

td = TDClient(apikey=API_KEY)

#Change the symbol of the ticker here
ts = td.time_series(
    symbol= TICKER,
    interval= INTERVAL,
    timezone="America/New_York",
    outputsize= 1
)


#Map the receive data
def get_data():
    tmp = ts.with_macd().with_macd(fast_period=10).with_stoch().as_pandas()
    data = tmp.to_dict(orient = 'record')
    timestamp = datetime.datetime.now().__str__()

    return{
     "datetime" : timestamp,
     "macd": data[0]['macd1'], 
     "macd_signal": data[0]['macd_signal1'], 
     "macd_hist":data[0]['macd_hist1']
    }


def run():
  
    iterator = 0
    print("Setting up Twelve producer at {}".format(KAFKA_BROKER_URL))
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        # Encode all values as JSON
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    )

    while True:
        sendit = get_data()
        # adding prints for debugging in logs
        print("Sending new Twelve data iteration - {}".format(iterator))
        print(sendit)
        producer.send(TOPIC_NAME, value= sendit)
        print("New Twelve data sent")
        time.sleep(SLEEP_TIME)
        print("Waking up!")
        iterator += 1


if __name__ == "__main__":
    run()