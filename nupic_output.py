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
"""
Provides two classes with the same signature for writing data out of NuPIC
models.
(This is a component of the One Hot Gym Prediction Tutorial.)
"""
import os
import csv
from collections import deque
from abc import ABCMeta, abstractmethod
from nupic.algorithms import anomaly_likelihood
# Try to import matplotlib, but we don't have to.
try:
  import matplotlib
  matplotlib.use('TKAgg')
  import matplotlib.pyplot as plt
  import matplotlib.gridspec as gridspec
  from matplotlib.dates import date2num
except ImportError:
  pass


WINDOW = 100
DEFAULT_OUTPUT_PATH = "."


class NuPICOutput(object):

  __metaclass__ = ABCMeta


  def __init__(self, name, predictedField, path=DEFAULT_OUTPUT_PATH):
    self.name = name
    self.predictedField = predictedField
    self.path = path


  @abstractmethod
  def write(self, row, result):
    pass


  @abstractmethod
  def close(self):
    pass



class NuPICFileOutput(NuPICOutput):


  def __init__(self, *args, **kwargs):
    super(NuPICFileOutput, self).__init__(*args, **kwargs)
    self.outputFile = None
    self.outputWriter = None
    self.lineCount = None
    self.lineCount = 0
    outputFilePath = os.path.join(self.path, "%s.csv" % self.name)
    print "Preparing to output %s data to %s" % (self.name, outputFilePath)
    self.outputFile = open(outputFilePath, "w")
    self.outputWriter = csv.writer(self.outputFile)
    self._headerWritten = False
    self.anomalyLikelihoodHelper = anomaly_likelihood.AnomalyLikelihood()



  def write(self, row, result):
    row["anomalyScore"] = result.inferences["anomalyScore"]
    if not self._headerWritten:
      keys = row.keys()
      keys.append("predicted")
      keys.append("anomalyLikelihood")
      self.outputWriter.writerow(keys)
      self._headerWritten = True
    predicted = result.inferences["multiStepBestPredictions"][1]
    value = row[self.predictedField]
    anomalyLikelihood = self.anomalyLikelihoodHelper.anomalyProbability(
      value, row["anomalyScore"], row["seconds"]
    )
    rows = row.values()
    rows.append(predicted)
    rows.append(anomalyLikelihood)
    self.outputWriter.writerow(rows)
    self.lineCount += 1



  def close(self):
    self.outputFile.close()
    print "Wrote %i data lines to %s." % \
          (self.lineCount, os.path.abspath(self.outputFile.name))



class NuPICPlotOutput(NuPICOutput):


  def __init__(self, *args, **kwargs):
    super(NuPICPlotOutput, self).__init__(*args, **kwargs)
    self.names = [self.name]
    # Turn matplotlib interactive mode on.
    plt.ion()
    self.dates = []
    self.convertedDates = []
    self.actualValues = []
    self.predictedValues = []
    self.actualLines = []
    self.predictedLines = []
    self.linesInitialized = False
    self.graphs = []
    plotCount = len(self.names)
    plotHeight = max(plotCount * 3, 6)
    fig = plt.figure(figsize=(14, plotHeight))
    gs = gridspec.GridSpec(plotCount, 1)
    for index in range(len(self.names)):
      self.graphs.append(fig.add_subplot(gs[index, 0]))
      plt.title(self.names[index])
      plt.ylabel('Frequency Bucket')
      plt.xlabel('Seconds')
    plt.tight_layout()



  def initializeLines(self, timestamps):
    for index in range(len(self.names)):
      print "initializing %s" % self.names[index]
      # graph = self.graphs[index]
      self.dates.append(deque([timestamps[index]] * WINDOW, maxlen=WINDOW))
      # print self.dates[index]
      # self.convertedDates.append(deque(
      #   [date2num(date) for date in self.dates[index]], maxlen=WINDOW
      # ))
      self.actualValues.append(deque([0.0] * WINDOW, maxlen=WINDOW))
      self.predictedValues.append(deque([0.0] * WINDOW, maxlen=WINDOW))

      actualPlot, = self.graphs[index].plot(
        self.dates[index], self.actualValues[index]
      )
      self.actualLines.append(actualPlot)
      predictedPlot, = self.graphs[index].plot(
        self.dates[index], self.predictedValues[index]
      )
      self.predictedLines.append(predictedPlot)
    self.linesInitialized = True



  def write(self, timestamps, actualValues, predictedValues,
            predictionStep=1):

    assert len(timestamps) == len(actualValues) == len(predictedValues)

    # We need the first timestamp to initialize the lines at the right X value,
    # so do that check first.
    if not self.linesInitialized:
      self.initializeLines(timestamps)

    for index in range(len(self.names)):
      self.dates[index].append(timestamps[index])
      # self.convertedDates[index].append(date2num(timestamps[index]))
      self.actualValues[index].append(actualValues[index])
      self.predictedValues[index].append(predictedValues[index])

      # Update data
      self.actualLines[index].set_xdata(self.dates[index])
      self.actualLines[index].set_ydata(self.actualValues[index])
      self.predictedLines[index].set_xdata(self.dates[index])
      self.predictedLines[index].set_ydata(self.predictedValues[index])

      self.graphs[index].relim()
      self.graphs[index].autoscale_view(True, True, True)

    plt.pause(0.000001) # This also calls draw()
    plt.legend(('actual','predicted'), loc=3)



  def close(self):
    plt.ioff()
    plt.show()



NuPICOutput.register(NuPICFileOutput)
