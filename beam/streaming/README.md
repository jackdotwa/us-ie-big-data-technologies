# Beam


## Getting started

  * update Sep 2024: Tested with Python 3.12

Install the required packages:
```
pip3 install -r requirements.txt
```

You may need to install the Google Cloud SDK but will be prompted typically if it is missing on your system.

### Pub/Sub emulator
The Pub/Sub emulator is initialized and handled by the _bash_ scripts in the `scripts` directory.

#### Initialize
To initialize the Pub/Sub emulator, run (MacOS)
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

To create a standalone Pub/Sub consumer (i.e. subscription) that listens for published messages, run (for example):
```
./custom_consumer.sh input_subscription
```
This consumer is handy as it illustrate that messages are read off the queue. Be sure to not leave it running.

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


### Assignment

Review the source to see where you might modify the code to your advantage, e.g. 

```
##
# For the sake of the assignment, you MUST use
# NUM_USERS = int(1e3)
# NUM_RECORDS = int(1e5)
# but feel free to change these for experimentation (fewer == easier to understand)
##
NUM_USERS = int(1e3)
NUM_RECORDS = int(1e5)
```

in `pubsub-emulator/messages.py`. You should be able to run this code in any Unix based system
(use docker if you need a sandbox). With these steps you will be able to run this code as is (see the `scripts` folder):

1. `./start_pubsub_emulator.sh`: this will occupy a terminal so keep extra one handy (or `./start_pubsub_emulator.sh &> /dev/null &` --- run in background and redirect output to null)
2. `./create_topics_subs.sh` 
3. `./custom_publisher.sh`: this too will occupy a terminal and you may want to see this output while experimenting (see the comments in the code about reducing the volume of messages)
4. `./assignment_run.sh`: you will see messages streaming through your terminal (preferably a second terminal).

If you struggle with the setup, pop us on Slack (as always).

The only files you will need to modify for experimentation are `pubsub-emulator/messages.py` and `assignment.py`. You will need to add to `assignment.py` to complete the tasks. 
