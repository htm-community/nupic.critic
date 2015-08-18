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

from nupic.data.inference_shifter import InferenceShifter
from nupic.frameworks.opf.modelfactory import ModelFactory

import nupic_output


MODEL_PARAMS_DIR = "./model_params"
PREDICTED_BUCKET = "b0"


def createModel(modelParams):
  model = ModelFactory.create(modelParams)
  model.enableInference({"predictedField": PREDICTED_BUCKET})
  return model



def getModelParamsFromName(modelName):
  importName = "model_params.%s_model_params" % (
    modelName.replace(" ", "_").replace("-", "_")
  )
  print "Importing model params from %s" % importName
  try:
    importedModelParams = importlib.import_module(importName).MODEL_PARAMS
  except ImportError:
    raise Exception("No model params exist for '%s'. Run swarm first!"
                    % modelName)
  return importedModelParams



def runIoThroughNupic(inputPath, model, modelName, plot=False):
  with open(inputPath, "rb") as inputFile:
    csvReader = csv.reader(inputFile)
    # skip header rows
    headers = csvReader.next()
    csvReader.next()
    csvReader.next()
    shifter = InferenceShifter()

    if plot:
      output = nupic_output.NuPICPlotOutput(modelName)
    else:
      output = nupic_output.NuPICFileOutput(modelName, path="data")

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
        actual = input_row[PREDICTED_BUCKET]
        shifter.shift(result)
        predicted = result.inferences["multiStepBestPredictions"][1]
        output.write([seconds], [actual], [predicted])
      else:
        output.write(input_row, result)

    output.close()



def runModel(input_path, plot):
  print "Creating model from %s..." % input_path
  modelName = os.path.splitext(os.path.basename(input_path))[0]
  outputName = modelName.split('_')[0]
  modelParams = getModelParamsFromName(modelName)
  model = createModel(modelParams)
  runIoThroughNupic(input_path, model, "%s_output" % outputName, plot)



if __name__ == "__main__":
  args = sys.argv[1:]
  input_path = args[0]
  plot = False
  if "--plot" in args:
    plot = True
  runModel(input_path, plot)
