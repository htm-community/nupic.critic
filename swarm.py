#!/usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------
"""
Groups together the code dealing with swarming.
(This is a component of the One Hot Gym Prediction Tutorial.)
"""
import os
import pprint

from nupic.swarming import permutations_runner
from swarm_description import SWARM_DESCRIPTION

INPUT_FILE = "reich_input.csv"



def modelParamsToString(modelParams):
  pp = pprint.PrettyPrinter(indent=2)
  return pp.pformat(modelParams)



def writeModelParamsToFile(modelParams, name):
  cleanName = name.replace(" ", "_").replace("-", "_")
  paramsName = "%s_model_params.py" % cleanName
  outDir = os.path.join(os.getcwd(), 'model_params')
  if not os.path.isdir(outDir):
    os.mkdir(outDir)
  outPath = os.path.join(os.getcwd(), 'model_params', paramsName)
  with open(outPath, "wb") as outFile:
    modelParamsString = modelParamsToString(modelParams)
    outFile.write("MODEL_PARAMS = \\\n%s" % modelParamsString)
  return outPath



def swarmForBestModelParams(swarmConfig, name, maxWorkers=4):
  outputLabel = name
  permWorkDir = os.path.abspath('swarm')
  if not os.path.exists(permWorkDir):
    os.mkdir(permWorkDir)
  modelParams = permutations_runner.runWithConfig(
    swarmConfig,
    {"maxWorkers": maxWorkers, "overwrite": True},
    outputLabel=outputLabel,
    outDir=permWorkDir,
    permWorkDir=permWorkDir,
    verbosity=0
  )
  modelParamsFile = writeModelParamsToFile(modelParams, name)
  return modelParamsFile



def printSwarmSizeWarning(size):
  if size is "small":
    print "= THIS IS A DEBUG SWARM. DON'T EXPECT YOUR MODEL RESULTS TO BE GOOD."
  elif size is "medium":
    print "= Medium swarm. Sit back and relax, this could take awhile."
  else:
    print "= LARGE SWARM! Might as well load up the Star Wars Trilogy."



def getSwarmDescription():
  for i in xrange(10):
    SWARM_DESCRIPTION["includedFields"].append({
      "fieldName": "b%i" % i,
      "fieldType": "float",
      "maxValue": 6000.0,
      "minValue": 0.0
    })
  return SWARM_DESCRIPTION



def swarm(filePath):
  name = os.path.splitext(os.path.basename(filePath))[0]
  print "================================================="
  print "= Swarming on %s data..." % name
  printSwarmSizeWarning(SWARM_DESCRIPTION["swarmSize"])
  print "================================================="
  swarmDescription = getSwarmDescription()
  modelParams = swarmForBestModelParams(swarmDescription, name)
  print "\nWrote the following model param files:"
  print "\t%s" % modelParams



if __name__ == "__main__":
  swarm(INPUT_FILE)