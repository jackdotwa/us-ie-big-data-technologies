# One image for your Python code: the Flink TaskManager, the Beam Python 3.10 SDK and your requirements.
# Flink starts the Python worker itself (environment_type=PROCESS), so if your code crashes or runs out of
# memory, Flink restarts the job from the last checkpoint and starts a fresh worker.
# Python 3.10 is pinned because the 3.12 SDK image crashes on arm64.
FROM flink:1.19.3-java11 AS flink

FROM apache/beam_python3.10_sdk:2.77.0
# Kafka admin client for scripts/create_topics.py and quick test producers.
RUN pip install --no-cache-dir confluent-kafka==2.6.0
RUN groupadd -g 9999 flink && useradd -u 9999 -g flink -d /opt/flink -s /bin/bash flink
COPY --from=flink /opt/java/openjdk /opt/java/openjdk
COPY --from=flink --chown=flink:flink /opt/flink /opt/flink
COPY --from=flink /docker-entrypoint.sh /docker-entrypoint.sh
COPY --from=flink /usr/local/bin/gosu /usr/bin/envsubst /usr/local/bin/
ENV FLINK_HOME=/opt/flink JAVA_HOME=/opt/java/openjdk DISABLE_JEMALLOC=true \
    PATH=/opt/flink/bin:/opt/java/openjdk/bin:$PATH \
    RUN_PYTHON_SDK_IN_DEFAULT_ENVIRONMENT=1
# Show the Python worker's own output (start-up errors, tracebacks) in `docker compose logs taskmanager`,
# and keep the Kafka client's per-poll INFO lines out of the log.
RUN printf '\nlogger.beamproc.name = org.apache.beam.runners.fnexecution.environment.ProcessManager\nlogger.beamproc.level = DEBUG\nlogger.kafka.name = org.apache.kafka\nlogger.kafka.level = WARN\n' \
    >> /opt/flink/conf/log4j-console.properties
# Your requirements come last, so changing them rebuilds only this layer.
COPY --from=job requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
# the Python worker writes its options file into the working directory, which must belong to flink
WORKDIR /opt/flink
ENTRYPOINT []
