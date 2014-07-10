#!/usr/bin/env python
import sys
import os
import csv
import time
import subprocess
from collections import deque
from optparse import OptionParser
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

WINDOW = 200


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


def run(input_dir, audio_file=None):
  file_names = os.listdir(input_dir)
  bins = [os.path.splitext(n)[0] for n in file_names]
  input_files = [open(os.path.join(input_dir, f)) for f in file_names]

  readers = [csv.reader(f) for f in input_files]

  headers = [reader.next() for reader in readers]
  for reader in readers:
    reader.next()
    reader.next()

  plt.ion()
  fig = plt.figure(figsize=(20, 10))
  gs = gridspec.GridSpec(2, 1)
  value_plot = fig.add_subplot(gs[0, 0])
  anomaly_plot = fig.add_subplot(gs[1, 0])
  anomaly_plot.set_ylim([-0.2, 1.2])

  data = []
  plots = {}

  for i, header in enumerate(headers):
    bin_data = {}
    for column in header:
      if column.startswith("anomaly"):
        column_name = "%s-%s" % (bins[i], column)
      else:
        column_name = column
      bin_data[column_name] = deque([0.0] * WINDOW, maxlen=WINDOW)
    data.append(bin_data)

  anomaly_legend = []
  # First, we initialize the chart with the first row of data.
  next_lines = [reader.next() for reader in readers]
  for i, row in enumerate(next_lines):
    # Initialize with first row.
    for row_index, row_value in enumerate(row):
      for header_index, hdr in enumerate(headers[i]):
        # Plots major input data, but not predictions
        if row_index == header_index:
          if hdr.startswith("b"):
            data[i][hdr].append(row_value)
            plots[hdr], = value_plot.plot(data[i][hdr])
          elif hdr.startswith("anomaly"):
            anomaly_label = "%s-%s" % (bins[i], hdr)
            data[i][anomaly_label].append(row_value)
            anomaly_legend.append(anomaly_label)
            color = "y"
            if hdr == "anomalyLikelihood":
              color = "r"
            plots[anomaly_label], = anomaly_plot.plot(data[i][anomaly_label], color)

  value_plot.legend(bins, loc=3)
  # anomaly_plot.legend(anomaly_legend, loc=3)
  plt.draw()
  plt.tight_layout()

  if audio_file:
    subprocess.call("open %s" % audio_file, shell=True)
    time.sleep(0.5)

  start = time.time()
  max_y_value = 0.0

  while True:
    try:
      next_lines = [reader.next() for reader in readers]
    except StopIteration:
      break

    for i, row in enumerate(next_lines):
      data_time = start + float(row[headers[i].index("seconds")])
      # Initialize with first row.
      for row_index, row_value in enumerate(row):
        for header_index, hdr in enumerate(headers[i]):

          # Plots major input data, but not predictions
          if row_index == header_index:
            label = hdr

            if hdr.startswith("anomaly"):
              label = "%s-%s" % (bins[i], hdr)
            data[i][label].append(row_value)

            if not label == "seconds" and label in plots:
              if float(row_value) > max_y_value:
                max_y_value = float(row_value)

              plot = plots[label]
              plot.set_xdata(data[i]["seconds"])
              plot.set_ydata(data[i][label])

    value_plot.set_ylim([0, max_y_value])
    value_plot.relim()
    value_plot.autoscale_view(True, True, True)
    anomaly_plot.relim()
    anomaly_plot.autoscale_view(True, True, True)
    plt.draw()

    if audio_file:
      while time.time() < data_time:
        time.sleep(0.1)


  for f in input_files:
    f.close()



if __name__ == "__main__":
  (options, args) = parser.parse_args(sys.argv[1:])
  try:
    input_dir = args.pop(0)
  except IndexError:
    parser.print_help(sys.stderr)

  audio_file = options.wav

  run(input_dir, audio_file)
