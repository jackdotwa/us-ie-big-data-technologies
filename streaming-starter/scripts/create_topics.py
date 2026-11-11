"""Create the topics named in the connection file on the local Kafka.
Run:  docker compose run --rm topics"""
import os
from confluent_kafka.admin import AdminClient, NewTopic

admin = AdminClient({"bootstrap.servers": os.environ["KAFKA_BOOTSTRAP"]})
partitions = {"EVENTS_TOPIC": 2}
compacted = {"REF_TOPIC"}
names = ["EVENTS_TOPIC", "CARD_EVENTS_TOPIC", "REF_TOPIC", "ALERTS_TOPIC",
         "AUDIT_REPLIES_TOPIC"]
existing = admin.list_topics(timeout=10).topics
new = [NewTopic(os.environ[n], partitions.get(n, 1), 1,
                config={"cleanup.policy": "compact"} if n in compacted else {})
       for n in names if os.environ.get(n) and os.environ[n] not in existing]
for topic, f in (admin.create_topics(new).items() if new else []):
    f.result()
    print("created", topic)
print("topics:", sorted(t for t in admin.list_topics(timeout=10).topics if not t.startswith("__")))
