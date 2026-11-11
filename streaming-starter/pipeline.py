"""Stack check: proves the stack works end to end on Flink. It is not a detector.
Reads both topics, counts records per topic per 1-minute window (by Kafka record time), and writes
each count to Postgres (table stackcheck) and to SeaweedFS (s3://$S3_BUCKET/stackcheck/...).
Look for STACKCHECK lines in: docker compose logs -f taskmanager
Replace it with your own job, and keep reading every setting from the environment."""
import json, logging, os, time
import apache_beam as beam
from apache_beam.io.kafka import ReadFromKafka
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms import window


def kafka_config():
    """Consumer settings from the connection file (see connection/)."""
    cfg = {"bootstrap.servers": os.environ["KAFKA_BOOTSTRAP"],
           "group.id": os.environ["CONSUMER_GROUP"], "auto.offset.reset": "earliest"}
    if os.environ.get("KAFKA_USERNAME"):
        cfg.update({
            "security.protocol": os.environ.get("KAFKA_SECURITY_PROTOCOL", "SASL_SSL"),
            "sasl.mechanism": os.environ.get("KAFKA_SASL_MECHANISM", "SCRAM-SHA-512"),
            "sasl.jaas.config": "org.apache.kafka.common.security.scram.ScramLoginModule required "
                                f'username="{os.environ["KAFKA_USERNAME"]}" '
                                f'password="{os.environ["KAFKA_PASSWORD"]}";'})
    return cfg


class StackOptions(PipelineOptions):
    """Options for Flink and for your job must be declared here, or the Python SDK drops them."""
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument("--checkpointing_interval", type=int, default=30000)  # ms
        # keep the latest checkpoint when the job is cancelled or fails, so you can resume from it
        parser.add_argument("--externalized_checkpoints_enabled", type=bool, default=True)
        parser.add_argument("--retain_externalized_checkpoints_on_cancellation", type=bool, default=True)
        # resume: --savepoint_path=/checkpoints/<old job id>/chk-<n>  (see the README)
        parser.add_argument("--savepoint_path", default=None)
        # which version of your code is running, e.g. --code_version=$(git describe --tags --always)
        parser.add_argument("--code_version", default="unknown")


class WriteCount(beam.DoFn):
    """Runs on the Python worker: connects once per worker, then writes each count."""
    def __init__(self, topic, code_version):
        self.topic, self.code_version = topic, code_version

    def setup(self):
        import boto3, psycopg
        self.pg = psycopg.connect(os.environ["PG_DSN"], autocommit=True)
        self.pg.execute("CREATE TABLE IF NOT EXISTS stackcheck (topic text, window_end timestamptz, n int, "
                        "code_version text, written_at timestamptz DEFAULT now(), "
                        "PRIMARY KEY (topic, window_end))")
        self.s3 = boto3.client("s3", endpoint_url=os.environ["S3_ENDPOINT"])
        try:
            self.s3.create_bucket(Bucket=os.environ["S3_BUCKET"])
        except self.s3.exceptions.ClientError:
            pass  # already there

    def process(self, n, w=beam.DoFn.WindowParam):
        end = w.end.to_utc_datetime()
        self.pg.execute("INSERT INTO stackcheck (topic, window_end, n, code_version) VALUES (%s, %s, %s, %s) "
                        "ON CONFLICT (topic, window_end) DO UPDATE SET n = EXCLUDED.n, "
                        "code_version = EXCLUDED.code_version, written_at = now()",
                        (self.topic, end, n, self.code_version))
        key = f"stackcheck/{self.topic}/{end:%Y%m%dT%H%M}.json"
        body = json.dumps({"n": n, "code_version": self.code_version}).encode()
        self.s3.put_object(Bucket=os.environ["S3_BUCKET"], Key=key, Body=body)
        logging.warning("STACKCHECK %s %d records/min code_version=%s -> postgres + s3://%s/%s",
                        self.topic, n, self.code_version, os.environ["S3_BUCKET"], key)

    def teardown(self):
        self.pg.close()


opts = StackOptions(save_main_session=False)
code_version = opts.view_as(StackOptions).code_version
cfg = kafka_config()
p = beam.Pipeline(options=opts)
for name in ("EVENTS_TOPIC", "CARD_EVENTS_TOPIC"):
    topic = os.environ[name]
    (p | f"read {name}" >> ReadFromKafka(consumer_config=cfg, topics=[topic],
                                         timestamp_policy=ReadFromKafka.create_time_policy,
                                         expansion_service="localhost:8097")
       | f"window {name}" >> beam.WindowInto(window.FixedWindows(60))
       | f"one {name}" >> beam.Map(lambda kv: 1)
       | f"count {name}" >> beam.CombineGlobally(sum).without_defaults()
       | f"write {name}" >> beam.ParDo(WriteCount(topic, code_version)))

# Submit and return once Flink has the job; it keeps running after this script exits.
# Stop it from the Flink UI (Cancel) or: curl -X PATCH "localhost:8081/jobs/<id>?mode=cancel"
result = p.run()
for _ in range(120):
    if str(result.state) in ("RUNNING", "FAILED", "CANCELLED", "DONE"):
        break
    time.sleep(1)
print("job state:", result.state)
