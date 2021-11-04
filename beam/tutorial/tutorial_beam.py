from __future__ import absolute_import
import argparse
import logging
import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

class Transform(beam.DoFn):
  # Use classes to perform transformations on your PCollections
  # Yeld or return the element(s) needed as input for the next transform
  def process(self, element):
      yield element


def run(argv=None, save_main_session=True):
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input',
      required=True,
      help='Input file to process.')
  parser.add_argument(
      '--output',
      dest='output',
      required=True,
      help='Output file to write results to.')
  known_args, pipeline_args = parser.parse_known_args(argv)

  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

  # Create the initial PCollection
  p = beam.Pipeline(options=pipeline_options)

  # Read the input file into a PCollection & perform transformations
  output = (
      p
      | 'read' >> ReadFromText(known_args.input)
      | 'transform' >> beam.ParDo(Transform())
      | 'write' >> WriteToText(known_args.output))

  result = p.run()
  result.wait_until_finish()

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
