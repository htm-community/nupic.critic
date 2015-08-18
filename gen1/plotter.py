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
import csv
import time
import subprocess
from collections import deque
# Try to import matplotlib, but we don't have to.
try:
  import matplotlib
  matplotlib.use('TKAgg')
  import matplotlib.pyplot as plt
  import matplotlib.gridspec as gridspec
  from matplotlib.dates import date2num
except ImportError:
  pass

WINDOW = 200


def run(input_file, audio_file=None):
  with open(input_file, "rb") as f:
    reader = csv.reader(f)

    headers = reader.next()
    reader.next()
    reader.next()
    plt.ion()
    fig = plt.figure(figsize=(20, 10))
    gs = gridspec.GridSpec(2, 1)
    value_plot = fig.add_subplot(gs[0, 0])

    data = {}
    plots = {}
    legend = []
    for header in headers:
      data[header] = deque([0.0] * WINDOW, maxlen=WINDOW)

    # Initialize with first row.
    row = reader.next()
    for row_index, row_value in enumerate(row):
      for header_index, hdr in enumerate(headers):

        # # Looks only at the predicted field, plotting actual and predicted
        # if hdr in ["b3", "predicted"] and row_index == header_index:
        #   data[hdr].append(row_value)
        #   plots[hdr], = plt.plot(data[hdr])

        # Plots major input data, but not predictions
        if hdr.startswith("b") \
            and row_index == header_index:
          data[hdr].append(row_value)
          plots[hdr], = plt.plot(data[hdr])
          legend.append(hdr)

      plt.legend(legend, loc=3)

    anomaly_plot = fig.add_subplot(gs[1, 0])
    anomaly_plot.set_ylim([-0.2, 1.2])
    plots["anomalyScore"], = plt.plot(data["anomalyScore"], 'y')
    plots["anomalyLikelihood"], = plt.plot(data["anomalyLikelihood"], 'r')

    plt.legend(["anomalyScore", "anomalyLikelihood"], loc=3)
    plt.draw()
    plt.tight_layout()

    
    if audio_file:
      subprocess.call("open %s" % audio_file, shell=True)
      time.sleep(0.5)

    start = time.time()
    max_y_value = 0.0

    for row in reader:
      data_time = start + float(row[headers.index("seconds")])
      for row_index, row_value in enumerate(row):
        for header_index, hdr in enumerate(headers):

          # # Looks only at the predicted field, plotting actual and predicted
          # if hdr in ["b3", "predicted", "seconds", "anomalyScore", "anomalyLikelihood"] \
          #         and row_index == header_index:
          #   data[hdr].append(row_value)
          #
          #   if hdr in ["b3", "predicted"]:
          #     if float(row_value) > max_y_value:
          #       max_y_value = float(row_value)
          #
          #   if not hdr == "seconds":
          #     plot = plots[hdr]
          #     plot.set_xdata(data["seconds"])
          #     plot.set_ydata(data[hdr])
          #     value_plot.set_ylim([0, max_y_value])


          # Plots major input data, but not predictions
          if hdr == "seconds" and row_index == header_index:
            data[hdr].append(row_value)

          elif (hdr.startswith("b") or hdr in ["anomalyScore", "anomalyLikelihood"]) \
            and row_index == header_index:
            data[hdr].append(row_value)
            if float(row_value) > max_y_value:
              max_y_value = float(row_value)
            plot = plots[hdr]
            plot.set_xdata(data["seconds"])
            plot.set_ydata(data[hdr])
            value_plot.set_ylim([0, max_y_value])

      value_plot.relim()
      value_plot.autoscale_view(True, True, True)
      anomaly_plot.relim()
      anomaly_plot.autoscale_view(True, True, True)
      plt.draw()

      if audio_file:
        while time.time() < data_time:
          time.sleep(0.1)

    plt.show()



if __name__ == "__main__":
  args = sys.argv[1:]
  input_file = args[0]
  audio_file = None
  if len(args) > 1:
    audio_file = args[1]
  run(input_file, audio_file)
