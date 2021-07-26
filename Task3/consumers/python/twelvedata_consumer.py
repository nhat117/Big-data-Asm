from kafka import KafkaConsumer
import os, json


if __name__ == "__main__":
    print("Starting Twelvedata Consumer")
    TOPIC_NAME = os.environ.get("TWELVEDATA_TOPIC_NAME", "twelve")
    KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", "localhost:9092")
    CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST", "localhost")
    CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE", "kafkapipeline")

    print("Setting up Kafka consumer at {}".format(KAFKA_BROKER_URL))
    consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=[KAFKA_BROKER_URL])
    
    print('Data is incomiingggggg...')
    for msg in consumer:
        msg = msg.value.decode('utf-8')
        jsonData=json.loads(msg)
        # add print for checking
        print(jsonData)
