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
import os
import sys
import csv
import importlib
from optparse import OptionParser

from nupic.data.inference_shifter import InferenceShifter
from nupic.frameworks.opf.model_factory import ModelFactory

import nupic_output


MODEL_PARAMS_DIR = "./model_params"
DEFAULT_MODEL_PARAMS_NAME = "grok_anomaly"
verbose = False


parser = OptionParser(
  usage="%prog <path/to/input/directory> [options]\n\nRun NuPIC on data "
        "generated from the 'convert_wav.py' script."
)

parser.add_option(
  "-m",
  "--model_params",
  dest="model_params_name",
  default=DEFAULT_MODEL_PARAMS_NAME,
  help="Name of the model params to use (without the '_model_params.py'). You "
       "won't need to set this unless you really know what you are doing.")
parser.add_option(
  "-p",
  "--plot",
  action="store_true",
  default=False,
  dest="plot",
  help="Plots the output instead of writing to file."
)
parser.add_option(
  "-v",
  "--verbose",
  action="store_true",
  default=False,
  dest="verbose",
  help="Print debugging statements.")
parser.add_option(
  "-s",
  "--save",
  action="store_true",
  default=False,
  dest="save",
  help="Will checkpoint the model after running so it can be reused later."
)
parser.add_option(
  "-r",
  "--resurrect",
  default=False,
  dest="resurrect",
  help="Uses specified model checkpoint instead of creating a new model using "
       "the model parameters. Learning will be automatically disabled on this "
       "model."
)


def create_model(model_params, bin):
  model = ModelFactory.create(model_params)
  model.enableInference({"predictedField": bin})
  return model



def resurrect_model(saved_model):
  return ModelFactory.loadFromCheckpoint(saved_model)



def get_model_params_from(model_name, bin):
  importName = "model_params.%s_model_params" % (
    model_name.replace(" ", "_").replace("-", "_")
  )
  print "Importing model params from %s for bin %s" % (importName, bin)
  try:
    importedModelParams = importlib.import_module(importName).MODEL_PARAMS
  except ImportError:
    raise Exception("No model params exist for '%s'!" % model_name)
  # Replace the field name with the bin name
  encoder = importedModelParams['modelParams']['sensorParams']['encoders']['REPLACE_ME']
  encoder['fieldname'] = bin
  encoder['name'] = bin
  # del importedModelParams['modelParams']['sensorParams']['encoders']['REPLACE_ME']
  importedModelParams['modelParams']['sensorParams']['encoders'][bin] = encoder
  return importedModelParams



def run_io_through_nupic(input_path, output_path, model, model_name, bin, plot):
  with open(input_path, "rb") as input_file:
    csvReader = csv.reader(input_file)
    # skip header rows
    headers = csvReader.next()
    csvReader.next()
    csvReader.next()
    shifter = InferenceShifter()

    if plot:
      output = nupic_output.NuPICPlotOutput(model_name, bin)
    else:
      output = nupic_output.NuPICFileOutput(model_name, bin, path=output_path)

    counter = 0
    for row in csvReader:
      assert len(row) == len(headers)
      counter += 1
      if (counter % 100 == 0):
        print "Read %i lines..." % counter
      row = [float(row[0])] + [int(val) for val in row[1:]]
      input_row = dict(zip(headers, row))
      result = model.run(input_row)

      if plot:
        seconds = input_row["seconds"]
        actual = input_row[bin]
        shifter.shift(result)
        predicted = result.inferences["multiStepBestPredictions"][1]
        output.write([seconds], [actual], [predicted])
      else:
        output.write(input_row, result)

    output.close()



def run_models(input_path, model_params_name, save, saved_models_dir, plot):
  for input_file in os.listdir(input_path):

    if verbose:
      print "Found input file %s" % input_file

    bin = os.path.splitext(input_file)[0]

    if saved_models_dir:
      print "Using models from %s for input %s..." \
            % (saved_models_dir, input_path)
      model = resurrect_model(os.path.join(saved_models_dir, bin))
      print "LEARNING IS DISABLED!"
      model.disableInference()
    else:
      print "Creating models from %s using %s_model_params..." \
            % (input_path, model_params_name)
      modelParams = get_model_params_from(model_params_name, bin)
      model = create_model(modelParams, bin)

    input_file_path = os.path.join(input_path, input_file)
    output_path = os.path.join(input_path, '../output')

    if not os.path.exists(output_path):
      os.makedirs(output_path)

    run_io_through_nupic(input_file_path, output_path, model, bin, bin, plot)

    if save:
      absolute_save_path = os.path.abspath(os.path.join(output_path, "saved_models", bin))
      model.save(absolute_save_path)
      print "Model checkpoint saved at %s." % absolute_save_path



if __name__ == "__main__":
  (options, args) = parser.parse_args(sys.argv[1:])
  try:
    input_path = args.pop(0)
  except IndexError:
    parser.print_help(sys.stderr)
    sys.exit()

  verbose = options.verbose

  run_models(
    input_path,
    options.model_params_name,
    options.save,
    options.resurrect,
    options.plot)
