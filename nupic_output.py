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
Provides two classes with the same signature for writing data out of NuPIC
models.
(This is a component of the One Hot Gym Prediction Tutorial.)
"""
import os
import csv
from collections import deque
from abc import ABCMeta, abstractmethod


WINDOW = 100
DEFAULT_OUTPUT_PATH = "."


class NuPICOutput(object):

  __metaclass__ = ABCMeta


  def __init__(self, name, path=DEFAULT_OUTPUT_PATH):
    self.name = name
    self.path = path


  @abstractmethod
  def write(row, result):
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



  def write(self, row, result):
    row["anomalyScore"] = result.inferences["anomalyScore"]
    if not self._headerWritten:
      self.outputWriter.writerow(row.keys())
      self._headerWritten = True
    self.outputWriter.writerow(row.values())
    self.lineCount += 1



  def close(self):
    self.outputFile.close()
    print "Done. Wrote %i data lines to %s." % (self.lineCount, self.outputFile)



NuPICOutput.register(NuPICFileOutput)
