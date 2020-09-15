#!/bin/bash

export PUBSUB_EMULATOR_HOST=localhost:8085

PUBSUB_PROJECT_ID=beam-demo
python ../pubsub-emulator/publisher.py ${PUBSUB_PROJECT_ID} create input_topic
#python ../pubsub-emulator/publisher.py ${PUBSUB_PROJECT_ID} create output_topic

python ../pubsub-emulator/subscriber.py ${PUBSUB_PROJECT_ID} create input_topic input_subscription
#python ../pubsub-emulator/subscriber.py ${PUBSUB_PROJECT_ID} create output_topic output_subscription
