from kafka import KafkaProducer
import json
from data import get_data
import time

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                         value_serializer=json_serializer)

if __name__ == "__main__":
    for i in range(10):
        session = get_data()
        print(session)
        producer.send("session", value=session)
        time.sleep(60)
        
    producer.close()
