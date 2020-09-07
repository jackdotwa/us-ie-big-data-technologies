# Beam


## Getting started

Install the required packages:
```
pip3 install -r requirements.txt
```

### Pub/Sub emulator
The Pub/Sub emulator is initialized and handled by the _bash_ scripts in the `scripts` directory.

#### Initialize
To initialize the Pub/Sub emulator, run
```
export JAVA_HOME=/Library/Internet\ Plug-Ins/JavaAppletPlugin.plugin/Contents/Home

./start_pubsub_emulator.sh
```

or on Ubuntu:
```
sudo apt-get install openjdk-8-jdk-headless google-cloud-sdk-pubsub-emulator
export JAVA_HOME='/usr/lib/jvm/java-8-openjdk-amd64'
```

#### Create Pub/Sub topics
To create an input and output topic and subscription, run:

```
./create_topics_subs.sh
```

#### Create a consumer
To create a standalone Pub/Sub consumer (i.e. subscription) that listens for published messages, run:
```
./custom_consumer.sh
```

#### Create a publisher
To create a Pub/Sub publisher that publishes messages to a topic, run:

```
./custom_publisher.sh
```

#### Cleanup the Pub/Sub emulator
To delete the Pub/Sub topics and subscriptions (only once you're done), run:

 ```
./cleanup.sh
```
