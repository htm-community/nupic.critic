#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

import sys
import os
from optparse import OptionParser
import re
import csv
import pprint
from nupic.swarming import permutations_runner


DEFAULT_PREDICTED_FIELD = "b0"
DEFAULT_OUTPUT_DIR = "data"
DEFAULT_SWARM_ITERATION_COUNT = 2000
DEFAULT_SWARM_SIZE = "medium"
DEFAULT_WORKERS = 4
verbose = False

SWARM_DESCRIPTION = {
  "includedFields": [
  ],
  "streamDef": {
    "info": "",
    "version": 1,
    "streams": [
      {
        "info": "",
        "source": "",
        "columns": [
          "*"
        ]
      }
    ]
  },

  "inferenceType": "TemporalAnomaly",
  "inferenceArgs": {
    "predictionSteps": [
      1
    ],
    "predictedField": None
  },
  "iterationCount": None,
  "swarmSize": None
}

parser = OptionParser(
  usage="%prog <path/to/input> [options]\n\nSwarm over NuPIC WAV input file."
)

parser.add_option(
    "-i",
    "--iteration_count",
    dest="iteration_count",
    default=DEFAULT_SWARM_ITERATION_COUNT,
    help="How many rows of input data to swarm over.")
parser.add_option(
    "-w",
    "--max_workers",
    dest="max_workers",
    default=DEFAULT_WORKERS,
    help="How many CPU processes to use.")
parser.add_option(
    "-p",
    "--predicted_field",
    dest="predicted_field",
    default=DEFAULT_PREDICTED_FIELD,
    help="Which field in the input is the field to predict?")
parser.add_option(
    "-o",
    "--output_directory",
    dest="output_dir",
    default=DEFAULT_OUTPUT_DIR,
    help="Directory to write the NuPIC input file.")
parser.add_option(
    "-s",
    "--swarm_size",
    dest="swarm_size",
    default=DEFAULT_SWARM_SIZE,
    help="How big should the swarm be? \"small\", \"medium\", or \"large\".")
parser.add_option(
  "-v",
  "--verbose",
  action="store_true",
  default=False,
  dest="verbose",
  help="Print debugging statements.")



def printSwarmSizeWarning(size):
  if size == "small":
    print "= THIS IS A DEBUG SWARM. DON'T EXPECT YOUR MODEL RESULTS TO BE GOOD."
  elif size == "medium":
    print "= Medium swarm. Sit back and relax, this could take awhile."
  else:
    print "= LARGE SWARM! Might as well load up the Star Wars Trilogy."



def extract_bucket_number_from_input_file(input_path):
  bucket_count = 0
  with open(input_path) as input_file:
    reader = csv.reader(input_file)
    headers = reader.next()
    for header in headers:
      if re.match("^b\d*$", header):
        bucket_count += 1
  return bucket_count



def get_swarm_description(
        name, input_path, predicted_field,
        iteration_count, swarm_size, buckets):
  for i in xrange(buckets):
    SWARM_DESCRIPTION["includedFields"].append({
      "fieldName": "b%i" % i,
      "fieldType": "float"
    })
  SWARM_DESCRIPTION["iterationCount"] = iteration_count
  SWARM_DESCRIPTION["swarmSize"] = swarm_size
  SWARM_DESCRIPTION["streamDef"]["info"] = name
  stream = SWARM_DESCRIPTION["streamDef"]["streams"][0]
  stream["info"] = name
  stream["source"] = "file://%s" % os.path.abspath(input_path)
  SWARM_DESCRIPTION["inferenceArgs"]["predictedField"] = predicted_field
  return SWARM_DESCRIPTION



def model_params_to_string(modelParams):
  pp = pprint.PrettyPrinter(indent=2)
  return pp.pformat(modelParams)



def write_model_params_to_file(modelParams, name):
  clean_name = name.replace(" ", "_").replace("-", "_")
  params_name = "%s_model_params.py" % clean_name
  out_dir = os.path.join(os.getcwd(), 'model_params')
  if not os.path.isdir(out_dir):
    os.mkdir(out_dir)
  out_path = os.path.join(os.getcwd(), 'model_params', params_name)
  with open(out_path, "wb") as outFile:
    model_params_string = model_params_to_string(modelParams)
    outFile.write("MODEL_PARAMS = \\\n%s" % model_params_string)
  return out_path



def swarm_for_best_model_params(swarm_config, name, max_workers):
  output_label = name
  perm_work_dir = os.path.abspath('swarm')
  if not os.path.exists(perm_work_dir):
    os.mkdir(perm_work_dir)
  if verbose:
    print "Using %i swarm workers." % max_workers
    print "\n** STARTING SWARM **\n\n"

  model_params = permutations_runner.runWithConfig(
    swarm_config,
    {"maxWorkers": max_workers, "overwrite": True},
    outputLabel=output_label,
    outDir=perm_work_dir,
    permWorkDir=perm_work_dir,
    verbosity=0
  )
  model_params_file = write_model_params_to_file(model_params, name)
  return model_params_file



def run(input_path, iteration_count, swarm_size,
        predicted_field, max_workers, output_dir):
  base_input_name = os.path.splitext(os.path.basename(input_path))[0]
  name = base_input_name + "_" + predicted_field
  buckets = extract_bucket_number_from_input_file(input_path)
  print "================================================="
  print "= Swarming on %s data..." % base_input_name
  if verbose:
    printSwarmSizeWarning(swarm_size)
    print "= Found %i buckets in %s" % (buckets, input_path)
  swarm_description = get_swarm_description(name, input_path, predicted_field,
                                         iteration_count, swarm_size, buckets)
  if verbose:
    print "= SWARM DESCRIPTION:"
    pprint.pprint(swarm_description)
  print "================================================="

  model_params = swarm_for_best_model_params(swarm_description,
                                             name, max_workers)
  print "\nWrote the following model params file:"
  print "\t%s" % model_params



if __name__ == "__main__":
  (options, args) = parser.parse_args(sys.argv[1:])
  try:
    input_path = args.pop(0)
  except IndexError:
    parser.print_help(sys.stderr)
    sys.exit()

  if not options.swarm_size in ["small", "medium", "large"]:
    raise ValueError("smarm_size must be 'small', 'medium', or 'large'.")

  verbose = options.verbose

  run(
    input_path,
    int(options.iteration_count),
    options.swarm_size,
    options.predicted_field,
    options.max_workers,
    options.output_dir
  )
