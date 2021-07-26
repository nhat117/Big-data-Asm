**This tutorial is part of my work for task 2 of assignment 1, i have reference guide from multiple sources listed in the references section of this file**

I Bui Minh Nhat s3878174 declare that my submission is conform with RMIT Policies. Part of this work is base on tutorial from [1], [2] [3]

# Link to my video : 


# This is a step by step guide to include Faker API into the built data pipeline based on [1] and [2].

**Note: if the tag "--build" not helping, add another tag "--force-recreate"**

# Quickstart instructions

You need to apply for some APIs to use with this. The APIs might take days for application to be granted access. Sample API keys are given, but it can be blocked if too many users are running this.

Twitter Developer API: https://developer.twitter.com/en/apply-for-access

OpenWeatherMap API: https://openweathermap.org/api 

After obtaining the API keys, please update the files  "twitter-producer/twitter_service.cfg" and "owm-producer/openweathermap_service.cfg" accordingly.


# Create docker networks

```bash
docker network create kafka-network                         # create a new docker network for kafka cluster (zookeeper, broker, kafka-manager services, and kafka connect sink services)

docker network create cassandra-network                     # create a new docker network for cassandra. (kafka connect will exist on this network as well in addition to kafka-network)
```


# 1.  Setting up Cassandra

Look at "faker-api/data.py", we can see the script to generate the fake data. We will worry about how to correctly set up the producer correctly later. There are 3 fields: name, address and year. We will set up Cassandra folder with this info.

Add these to a new schema file "cassandra/schema-faker.cql"

# Note: You could add more fields and specified their data type accordingly. More about fakerAPI DataField [4] : https://faker.readthedocs.io/en/master/providers.html

```
USE kafkapipeline;
CREATE TABLE IF NOT EXISTS kafkapipeline.fakerdata (
#Add_your_custom_attributes_here!!!!
);
```

Full Example: 

```
USE kafkapipeline;
CREATE TABLE IF NOT EXISTS kafkapipeline.fakerdata (
  name TEXT,
  address TEXT,
  year INT,
  phone_number TEXT,
  credit_card_number TEXT,
  company_name TEXT,
  city TEXT,
  job_name TEXT,
  user_agent TEXT,
  bank TEXT,
  PRIMARY KEY (name, address)
);
```

Now, add that file to the Dockerfile COPY line accordingly and rebuild the docker container Cassandra with the tag --build

```bash
docker-compose -f cassandra/docker-compose.yml up -d --build
```

Then go inside the Cassandra container and run 

```bash
cqlsh -f schema-faker.cql
```

To check the current database

```bash
$ cqlsh --cqlversion=3.4.4 127.0.0.1 #make sure you use the correct cqlversion

cqlsh> use kafkapipeline; #keyspace name

cqlsh:kafkapipeline> select * from twitterdata;

cqlsh:kafkapipeline> select * from weatherreport;

cqlsh:kafkapipeline> select * from fakerdata;

```
Voila you have successfully create faker schema with your data attributes.

# 2. Setting up Kafka Connect

In the folder "kafka", add this to the "connect/create-cassandra-sink.sh"


```
echo "Starting Faker Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "fakersink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "faker",
    "contactPoints": "cassandradb",
    "loadBalancing.localDc": "datacenter1",
    "topic.faker.kafkapipeline.fakerdata.mapping": "map_your_data_from_faker_producer_to_faker_schema_here!!!!",
    "topic.faker.kafkapipeline.fakerdata.consistencyLevel": "LOCAL_QUORUM"
  }
}'
echo "Done."
```
In the line contains, map the data coming from faker_producer to the specific data attributes that we have create early in schema-faker.cql.

```
    "topic.faker.kafkapipeline.fakerdata.mapping": "name=value.name, address=value.address, year=value.year, phone_number = value.phone_number, credit_card_number = value.credit_card_number, company_name = value.company_name, city = value.city, job_name = value.job_name, user_agent = value.user_agent, bank = value.bank",
```

Example :
```
echo "Starting Faker Sink"
curl -s \
     -X POST http://localhost:8083/connectors \
     -H "Content-Type: application/json" \
     -d '{
  "name": "fakersink",
  "config": {
    "connector.class": "com.datastax.oss.kafka.sink.CassandraSinkConnector",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",  
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable":"false",
    "tasks.max": "10",
    "topics": "faker",
    "contactPoints": "cassandradb",
    "loadBalancing.localDc": "datacenter1",
    "topic.faker.kafkapipeline.fakerdata.mapping": "name=value.name, address=value.address, year=value.year, phone_number = value.phone_number, credit_card_number = value.credit_card_number, company_name = value.company_name, city = value.city, job_name = value.job_name, user_agent = value.user_agent, bank = value.bank",
    "topic.faker.kafkapipeline.fakerdata.consistencyLevel": "LOCAL_QUORUM"
  }
}'
echo "Done."
```

Now, rebuild the docker container kafka with the tag --build

```bash
docker-compose -f kafka/docker-compose.yml up -d --build
```

Run the script inside "kafka-connect" container bash

```bash
./start-and-wait.sh
```
Create cluster on the UI by access http://localhost:9000

# 3. Setting up faker-producer

Duplicate the "own-producer" folder to get us some guiding code, rename it to "faker-producer". Inside that folder, delete the "openweathermap_service.cfg" since we don't need it anymore, rename the python file to "faker_producer.py". Now let's update each file one by one.

3.1. "faker-producer.py": 
- delete line 14-30 and 45-52
- add all from "faker-api/data.py" in
- update the file to make the program run correctly
- remove dataprep package
- here is the complete code for you reference:

```
"""Produce openweathermap content to 'faker' kafka topic."""
import asyncio
import configparser
import os
import time
from collections import namedtuple
from kafka import KafkaProducer
from faker import Faker
import json

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 5))

fake = Faker()

def get_registered_user():
    return {
# Add your data attributes corresponding to schema_faker and faker_api here
   }

def run():
    iterator = 0
    print("Setting up Faker producer at {}".format(KAFKA_BROKER_URL))
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        # Encode all values as JSON
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    )

    while True:
        sendit = get_registered_user()
        # adding prints for debugging in logs
        print("Sending new faker data iteration - {}".format(iterator))
        producer.send(TOPIC_NAME, value=sendit)
        print("New faker data sent")
        time.sleep(SLEEP_TIME)
        print("Waking up!")
        iterator += 1


if __name__ == "__main__":
    run()
```

At line 19 Mapping the corresponding data attribute from  schema-faker to faker api :

```
        "name": fake.name(),
        "address": fake.address(),
        "year": fake.year(),
        "phone_number": fake.phone_number(),
        "credit_card_number": fake.credit_card_number(),
        "company_name": fake.company(),
        "city": fake.city(),
        "job_name": fake.job(),
        "user_agent": fake.user_agent(),
        "bank": fake.iban()
```

Full Example Content :

```
"""Produce openweathermap content to 'faker' kafka topic."""
import asyncio
import configparser
import os
import time
from collections import namedtuple
from kafka import KafkaProducer
from faker import Faker
import json

KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL")
TOPIC_NAME = os.environ.get("TOPIC_NAME")
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 5))

fake = Faker()

def get_registered_user():
    return {
        "name": fake.name(),
        "address": fake.address(),
        "year": fake.year(),
        "phone_number": fake.phone_number(),
        "credit_card_number": fake.credit_card_number(),
        "company_name": fake.company(),
        "city": fake.city(),
        "job_name": fake.job(),
        "user_agent": fake.user_agent(),
        "bank": fake.iban()
    }

def run():
    iterator = 0
    print("Setting up Faker producer at {}".format(KAFKA_BROKER_URL))
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER_URL],
        # Encode all values as JSON
        value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    )

    while True:
        sendit = get_registered_user()
        # adding prints for debugging in logs
        print("Sending new faker data iteration - {}".format(iterator))
        producer.send(TOPIC_NAME, value=sendit)
        print("New faker data sent")
        time.sleep(SLEEP_TIME)
        print("Waking up!")
        iterator += 1


if __name__ == "__main__":
    run()
```

3.2. "requirements.txt": 
Replace dataprep with faker since we need the faker Python package

3.3. "Dockerfile": 
Rename python file to "faker_producer.py"

3.4. "docker-compose.yml":
- update line 4,5, and 9 to faker
- update SLEEP_TIME to 5

Full content
```
version: '3'

services:
  faker:
    container_name: faker
    build: .
    environment:
      KAFKA_BROKER_URL: broker:9092
      TOPIC_NAME: faker
      SLEEP_TIME: 5

networks:
  default:
    external:
      name: kafka-network

```

Now, build the new faker producer

```bash
docker-compose -f faker-producer/docker-compose.yml up -d
```


# 4. Setting up consumers

4.1. "faker_consumer.py": 

Duplicate the file "consumers/python/weather_consumer.py", rename it to "faker_consumer.py"

- Update multiple lines in there to clean up old "weather" code
- The two most important one is changing TOPIC_NAME = os.environ.get("FAKER_TOPIC_NAME", "faker") and encode('utf-8). 

Full code: 

```
from kafka import KafkaConsumer
import os, json


if __name__ == "__main__":
    print("Starting Faker Consumer")
    TOPIC_NAME = os.environ.get("FAKER_TOPIC_NAME", "faker")
    KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", "localhost:9092")
    CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST", "localhost")
    CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE", "kafkapipeline")

    print("Setting up Kafka consumer at {}".format(KAFKA_BROKER_URL))
    consumer = KafkaConsumer(TOPIC_NAME, bootstrap_servers=[KAFKA_BROKER_URL])
    
    print('Waiting for msg...')
    for msg in consumer:
        msg = msg.value.decode('utf-8')
        jsonData=json.loads(msg)
        # add print for checking
        print(jsonData)
  
  
```

4.2. "consumers/docker-compose.yml"

Add these in

```
  fakerconsumer:
    container_name: fakerconsumer
    image: twitterconsumer
    environment:
      KAFKA_BROKER_URL: broker:9092
      TOPIC_NAME: faker
      CASSANDRA_HOST: cassandradb
      CASSANDRA_KEYSPACE: kafkapipeline
    command: ["python", "-u","python/faker_consumer.py"]
```
Full Example Content :
```
version: '3'
  tweetconsumer:
    container_name: twitterconsumer
    image: twitterconsumer
    build: .
    environment:
      KAFKA_BROKER_URL: broker:9092
      TOPIC_NAME: twitter
      SINK_TOPIC_NAME: twittersink
      SLEEP_TIME: 10
      BATCH_SIZE: 10
  weatherconsumer:
    container_name: weatherconsumer
    image: twitterconsumer
    environment:
      KAFKA_BROKER_URL: broker:9092
      TOPIC_NAME: weather
      CASSANDRA_HOST: cassandradb
      CASSANDRA_KEYSPACE: kafkapipeline
    command: ["python", "-u","python/weather_consumer.py"]
  fakerconsumer:
    container_name: fakerconsumer
    image: twitterconsumer
    environment:
      KAFKA_BROKER_URL: broker:9092
      TOPIC_NAME: faker
      CASSANDRA_HOST: cassandradb
      CASSANDRA_KEYSPACE: kafkapipeline
    command: ["python", "-u","python/faker_consumer.py"]
networks:
  default:
    external:
      name: kafka-network

```
Now, rebuild the consumers with tag --build

```bash
docker-compose -f consumers/docker-compose.yml up --build
```

# 5. Check data in Cassandra
First login into Cassandra's container with the following command or open a new CLI from Docker Desktop if you use that.

```bash
docker exec -it cassandra bash
```

Once logged in, bring up cqlsh with this command and query twitterdata and weatherreport tables like this:

```bash
cqlsh --cqlversion=3.4.4 127.0.0.1 #make sure you use the correct cqlversion

cqlsh> use kafkapipeline; #keyspace name

cqlsh:kafkapipeline> select * from twitterdata;

cqlsh:kafkapipeline> select * from weatherreport;

cqlsh:kafkapipeline> select * from fakerdata;
```

Congratulation you have complete setsett up data pipe line for fakerAPI.

# 6. Setting up data-vis:

- Add this to "data-vis/docker-compose.yml"

```
FAKER_TABLE: fakerdata
```

Full content:

```
version: "3"

services:
  datavis:
    container_name: datavis
    hostname: datavis
    build:
      context: .
    environment:
      CASSANDRA_HOST: cassandradb
      CASSANDRA_KEYSPACE: kafkapipeline
      WEATHER_TABLE: weatherreport
      FAKER_TABLE: fakerdata
      TWITTER_TABLE: twitterdata
    ports:
        - 8888:8888
    volumes:
      - $PWD/data-vis/python:/usr/app
networks:
  default:
    external:
      name: cassandra-network

```

- In the file "data-vis/python/cassandrautils.py" replace the content of the file with the following code

```
import datetime
import gzip
import os
import re
import sys

import pandas as pd
from cassandra.cluster import BatchStatement, Cluster, ConsistencyLevel
from cassandra.query import dict_factory

tablename = os.getenv("weather.table", "weatherreport")
twittertable = os.getenv("twittertable.table", "twitterdata")
fakertable = os.getenv("fakertable.table", "fakerdata")


CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST") if os.environ.get("CASSANDRA_HOST") else 'localhost'
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE") if os.environ.get("CASSANDRA_KEYSPACE") else 'kafkapipeline'

WEATHER_TABLE = os.environ.get("WEATHER_TABLE") if os.environ.get("WEATHER_TABLE") else 'weather'
TWITTER_TABLE = os.environ.get("TWITTER_TABLE") if os.environ.get("TWITTER_TABLE") else 'twitter'
FAKER_TABLE = os.environ.get("FAKER_TABLE") if os.environ.get("FAKER_TABLE") else 'faker'

def saveTwitterDf(dfrecords):
    if isinstance(CASSANDRA_HOST, list):
        cluster = Cluster(CASSANDRA_HOST)
    else:
        cluster = Cluster([CASSANDRA_HOST])

    session = cluster.connect(CASSANDRA_KEYSPACE)

    counter = 0
    totalcount = 0

    cqlsentence = "INSERT INTO " + twittertable + " (tweet_date, location, tweet, classification) \
                   VALUES (?, ?, ?, ?)"
    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    insert = session.prepare(cqlsentence)
    batches = []
    for idx, val in dfrecords.iterrows():
        batch.add(insert, (val['datetime'], val['location'],
                           val['tweet'], val['classification']))
        counter += 1
        if counter >= 100:
            print('inserting ' + str(counter) + ' records')
            totalcount += counter
            counter = 0
            batches.append(batch)
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    if counter != 0:
        batches.append(batch)
        totalcount += counter
    rs = [session.execute(b, trace=True) for b in batches]

    print('Inserted ' + str(totalcount) + ' rows in total')


def saveFakerDf(dfrecords):
    if isinstance(CASSANDRA_HOST, list):
        cluster = Cluster(CASSANDRA_HOST)
    else:
        cluster = Cluster([CASSANDRA_HOST])

    session = cluster.connect(CASSANDRA_KEYSPACE)

    counter = 0
    totalcount = 0

    cqlsentence = "INSERT INTO " + fakertable + " (name, address, year) \
                   VALUES (?, ?, ?)"
    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    insert = session.prepare(cqlsentence)
    batches = []
    for idx, val in dfrecords.iterrows():
        batch.add(insert, (val['name'], val['address'],
                           val['year']))
        counter += 1
        if counter >= 100:
            print('inserting ' + str(counter) + ' records')
            totalcount += counter
            counter = 0
            batches.append(batch)
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    if counter != 0:
        batches.append(batch)
        totalcount += counter
    rs = [session.execute(b, trace=True) for b in batches]

    print('Inserted ' + str(totalcount) + ' rows in total')

def saveWeatherreport(dfrecords):
    if isinstance(CASSANDRA_HOST, list):
        cluster = Cluster(CASSANDRA_HOST)
    else:
        cluster = Cluster([CASSANDRA_HOST])

    session = cluster.connect(CASSANDRA_KEYSPACE)

    counter = 0
    totalcount = 0

    cqlsentence = "INSERT INTO " + tablename + " (forecastdate, location, description, temp, feels_like, temp_min, temp_max, pressure, humidity, wind, sunrise, sunset) \
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    insert = session.prepare(cqlsentence)
    batches = []
    for idx, val in dfrecords.iterrows():
        batch.add(insert, (val['report_time'], val['location'], val['description'],
                           val['temp'], val['feels_like'], val['temp_min'], val['temp_max'],
                           val['pressure'], val['humidity'], val['wind'], val['sunrise'], val['sunset']))
        counter += 1
        if counter >= 100:
            print('inserting ' + str(counter) + ' records')
            totalcount += counter
            counter = 0
            batches.append(batch)
            batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    if counter != 0:
        batches.append(batch)
        totalcount += counter
    rs = [session.execute(b, trace=True) for b in batches]

    print('Inserted ' + str(totalcount) + ' rows in total')


def loadDF(targetfile, target):
    if target == 'weather':
        colsnames = ['description', 'temp', 'feels_like', 'temp_min', 'temp_max',
                     'pressure', 'humidity', 'wind', 'sunrise', 'sunset', 'location', 'report_time']
        dfData = pd.read_csv(targetfile, header=None,
                             parse_dates=True, names=colsnames)
        dfData['report_time'] = pd.to_datetime(dfData['report_time'])
        saveWeatherreport(dfData)
    elif target == 'twitter':
        colsnames = ['tweet', 'datetime', 'location', 'classification']
        dfData = pd.read_csv(targetfile, header=None,
                             parse_dates=True, names=colsnames)
        dfData['datetime'] = pd.to_datetime(dfData['datetime'])
        saveTwitterDf(dfData)
    elif target == 'faker':
        colsnames = ['name', 'address', 'year']
        dfData = pd.read_csv(targetfile, header=None,
                             parse_dates=True, names=colsnames)
        saveFakerDf(dfData)


def getWeatherDF():
    return getDF(WEATHER_TABLE)
def getTwitterDF():
    return getDF(TWITTER_TABLE)
def getFakerDF():
    print(FAKER_TABLE)
    return getDF(FAKER_TABLE)

def getDF(source_table):
    if isinstance(CASSANDRA_HOST, list):
        cluster = Cluster(CASSANDRA_HOST)
    else:
        cluster = Cluster([CASSANDRA_HOST])

    if source_table not in (WEATHER_TABLE, TWITTER_TABLE, FAKER_TABLE):
        return None

    session = cluster.connect(CASSANDRA_KEYSPACE)
    session.row_factory = dict_factory
    cqlquery = "SELECT * FROM " + source_table + ";"
    rows = session.execute(cqlquery)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    action = sys.argv[1]
    target = sys.argv[2]
    targetfile = sys.argv[3]
    if action == "save":
        loadDF(targetfile, target)
    elif action == "get":
        getDF(target)
```

To put up the data-vis container

```bash
docker-compose -f data-vis/docker-compose.yml up -d --build
```
To access the jupyter notebook use the following address : http://localhost:8888/

In jupyter notebook, click on the blog-visuals.ipynb on the side bar

Add the following code in to new blank line :
```
faker = getFakerDF() #Retrieve the data
```

```
faker #Display the faker table
```
And that is it!!! Enjoy 3:

# 7. Follow the solution GitHub repo instruction for tear down.

To stop all running kakfa cluster services

```bash
$ docker-compose -f data-vis/docker-compose.yml down # stop visualization node

$ docker-compose -f consumers/docker-compose.yml down          # stop the consumers

$ docker-compose -f owm-producer/docker-compose.yml down       # stop open weather map producer

$ docker-compose -f faker-producer/docker-compose.yml down       # stop faker producer

$ docker-compose -f twitter-producer/docker-compose.yml down   # stop twitter producer

$ docker-compose -f kafka/docker-compose.yml down              # stop zookeeper, broker, kafka-manager and kafka-connect services

$ docker-compose -f cassandra/docker-compose.yml down          # stop Cassandra
```

To remove the kafka-network network:

```bash
$ docker network rm kafka-network
$ docker network rm cassandra-network
```

To remove resources in Docker

```bash
$ docker container prune # remove stopped containers, done with the docker-compose down
$ docker volume prune # remove all dangling volumes (delete all data from your Kafka and Cassandra)
$ docker image prune -a # remove all images (help with rebuild images)
$ docker builder prune # remove all build cache (you have to pull data again in the next build)
$ docker system prune -a # basically remove everything
```
# References

[1]N. Yen, "How to Build a Distributed Big Data Pipeline Using Kafka, Cassandra, and Jupyter Lab with Docker plus Faker API", GitHub, 2021. [Online]. Available: https://github.com/vnyennhi/docker-kafka-cassandra-faker-api. [Accessed: 21- Jul- 2021].

[2]N. Yen, "Step by step guide to include Faker API into the built data pipeline", GitHub, 2021. [Online]. Available: https://github.com/vnyennhi/docker-kafka-cassandra/blob/main/faker_api/README-tut4.md. [Accessed: 21- Jul- 2021].

[3]N. Yen, "docker-kafka-cassandra/README-tut4.md at main · vnyennhi/docker-kafka-cassandra", GitHub, 2021. [Online]. Available: https://github.com/vnyennhi/docker-kafka-cassandra/blob/main/cassandra/README-tut4.md. [Accessed: 21- Jul- 2021].

[4]D. Faraglia, "Standard Providers — Faker 8.10.1 documentation", Faker.readthedocs.io, 2021. [Online]. Available: https://faker.readthedocs.io/en/master/providers.html. [Accessed: 23- Jul- 2021].

