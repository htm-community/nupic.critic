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
import csv
import time
import subprocess
from optparse import OptionParser
from plot_output import NuPICPlotOutput

WINDOW = 200
HIGHLIGHT_ALPHA = 0.3
ANOMALY_HIGHLIGHT_COLOR = 'red'
DEFAULT_ANOMALY_THRESHOLD = 0.9
DEFAULT_ANOMALY_TRIGGER_COUNT = 1


parser = OptionParser(
  usage="%prog <path/to/nupic/output/directory> [options]\n\nPlot nupic "
        "output, optionally syncing the output to the playing of the original WAV file."
)

parser.add_option(
  "-w",
  "--wav",
  dest="wav",
  default=None,
  help="Path to a WAV file to play synced to the plot.")
parser.add_option(
  "-m",
  "--maximize",
  action="store_true",
  default=False,
  dest="maximize",
  help="Maximize plot window."
)
parser.add_option(
  "-t",
  "--anomaly_threshold",
  dest="anomaly_threshold",
  default=DEFAULT_ANOMALY_THRESHOLD,
  help="Value the anomaly likelihood(s) must breach before being marked as "
       "anomalous in the chart."
)
parser.add_option(
  "-g",
  "--anomaly_trigger",
  dest="anomaly_trigger",
  default=DEFAULT_ANOMALY_TRIGGER_COUNT,
  help="How many bins must be above the anomaly threshold to display an "
       "anomaly on the chart."
)
parser.add_option(
  "-a",
  "--use_anomaly_score",
  action="store_true",
  default=False,
  dest="use_anomaly_score",
  help="Use the anomalyScore from NuPIC instead of the anomalyLikelihood."
)


def run(input_dir, audio_file, maximize,
        anomaly_threshold, anomaly_trigger_count, use_anomaly_score):
  file_names = os.listdir(input_dir)
  bins = [os.path.splitext(n)[0] for n in file_names]
  input_files = [open(os.path.join(input_dir, f)) for f in file_names]

  readers = [csv.reader(f) for f in input_files]

  headers = [reader.next() for reader in readers]
  for reader in readers:
    reader.next()
    reader.next()

  output = NuPICPlotOutput(input_dir, bins, maximize, anomaly_threshold, anomaly_trigger_count)

  if audio_file:
    subprocess.call("open %s" % audio_file, shell=True)
    time.sleep(1.0)

  start = time.time()

  while True:
    try:
      next_lines = [reader.next() for reader in readers]
    except StopIteration:
      break

    seconds = float(next_lines[0][headers[0].index("seconds")])
    data_time = start + seconds

    bin_values = []
    anomaly_likelihoods = []

    if time.time() <= data_time:
      for i, line in enumerate(next_lines):
        freq_bin = bins[i]
        header = headers[i]
        bin_value = float(line[header.index(freq_bin)])
        if use_anomaly_score:
          anomaly_key = "anomalyScore"
        else:
          anomaly_key = "anomalyLikelihood"
        anomaly_likelihood = float(line[header.index(anomaly_key)])
        bin_values.append(bin_value)
        anomaly_likelihoods.append(anomaly_likelihood)
  
      output.write(seconds, bin_values, anomaly_likelihoods)
  
    # If syncing to an audio file, wait for it to catch up.
    if audio_file:
      while time.time() < data_time:
        time.sleep(0.1)


  output.close()
  for f in input_files:
    f.close()



if __name__ == "__main__":
  (options, args) = parser.parse_args(sys.argv[1:])
  try:
    input_dir = args.pop(0)
  except IndexError:
    parser.print_help(sys.stderr)

  audio_file = options.wav

  run(
    input_dir,
    audio_file,
    options.maximize,
    float(options.anomaly_threshold),
    int(options.anomaly_trigger),
    options.use_anomaly_score
  )
