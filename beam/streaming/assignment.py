import apache_beam as beam
import apache_beam.transforms.window as window
from apache_beam.io import ReadFromPubSub
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.transforms.trigger import AfterProcessingTime, AccumulationMode

import argparse
import datetime
import logging

logging.basicConfig(
    format="%(asctime)s : %(levelname)s : %(name)s : %(message)s", level=logging.INFO
)
logging = logging.getLogger(__name__)


class JobOptions(PipelineOptions):
    """
    these are commmand line options for cli usage
    """
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument("--input", required=True, help="pubsub input topic")

def custom_timestamp(message):
    """
    you need to tell Beam which field is your event time. This stub is assuming the 'message' is
    a row with a field 'timestamp', which is being indexed here. Do here as you wish.
    :param message:
    :return:
    """
    # ts = datetime.datetime.strptime(message['timestamp'], "%Y-%m-%d %H:%M:%S")
    ts = None
    return beam.window.TimestampedValue(message, ts.timestamp())


def run(argv=None, save_main_session=True):
    """
    run function to process cli args and run your program
    :param argv:
    :param save_main_session:
    :return:
    """

    parser = argparse.ArgumentParser()
    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    job_options = pipeline_options.view_as(JobOptions)


    logging.info("-----------------------------------------------------------")
    logging.info("               Streaming with Pub/Sub emulator             ")
    logging.info("-----------------------------------------------------------")


    source = ReadFromPubSub(subscription=str(job_options.input))

    ###
    #  STREAMING BEAM: add the necessary pipeline stages along with whatever functions you require in this file
    ###
    p = beam.Pipeline(options=pipeline_options)
    lines = (
        p
        | "read" >> source
        | beam.Map(print)
    )
    result = p.run()
    result.wait_until_finish()

if __name__ == "__main__":
    run()
