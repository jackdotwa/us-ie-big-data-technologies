#!/bin/bash
export PUBSUB_EMULATOR_HOST=localhost:8085

PUBSUB_PROJECT_ID=beam-demo
python ../assignment.py \
	--runner Direct \
	--input projects/${PUBSUB_PROJECT_ID}/subscriptions/input_subscription \
	--streaming
#	--output projects/${PUBSUB_PROJECT_ID}/topics/output_topic \
