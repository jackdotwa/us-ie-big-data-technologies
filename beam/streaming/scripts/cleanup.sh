#!/bin/bash

export PUBSUB_EMULATOR_HOST=localhost:8085

PUBSUB_PROJECT_ID=beam-demo
python ../pubsub-emulator/publisher.py ${PUBSUB_PROJECT_ID} delete input_topic
python ../pubsub-emulator/publisher.py ${PUBSUB_PROJECT_ID} delete output_topic

python ../pubsub-emulator/subscriber.py ${PUBSUB_PROJECT_ID} delete input_subscription
python ../pubsub-emulator/subscriber.py ${PUBSUB_PROJECT_ID} delete output_subscription

