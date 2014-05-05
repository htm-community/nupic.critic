#!/usr/bin/env python
import sys
import os
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

WINDOW = 100


def run(input_file, audio_file=None):
  with open(input_file, "rb") as f:
    reader = csv.reader(f)

    headers = reader.next()
    reader.next()
    reader.next()
    plt.ion()
    fig = plt.figure(figsize=(14, 6))
    gs = gridspec.GridSpec(2, 1)
    value_plot = fig.add_subplot(gs[0, 0])

    data = {}
    plots = {}
    for header in headers:
      data[header] = deque([0.0] * WINDOW, maxlen=WINDOW)

    # Initialize with first row.
    row = reader.next()
    for row_index, row_value in enumerate(row):
      for header_index, hdr in enumerate(headers):
        if not hdr == "anomalyScore" \
          and not hdr in ["b0", "b1", "b2", "b4", "b5", "b7", "b8"] \
          and row_index == header_index:
          data[hdr].append(row_value)
          plots[hdr], = plt.plot(data[hdr])
    
    anomaly_plot = fig.add_subplot(gs[1, 0])
    plots["anomalyScore"], = plt.plot(data["anomalyScore"], 'r')

    plt.draw()
    plt.tight_layout()

    start = time.time()
    
    if audio_file:
      subprocess.call("open %s" % audio_file, shell=True)

    for row in reader:
      data_time = start + float(row[headers.index("seconds")])
      for row_index, row_value in enumerate(row):
        for header_index, hdr in enumerate(headers):
          if not hdr in ["b0", "b1", "b2", "b4", "b5", "b7", "b8"] \
            and row_index == header_index:
            data[hdr].append(row_value)
            plot = plots[hdr]
            plot.set_xdata(data["seconds"])
            plot.set_ydata(data[hdr])
            if hdr == "anomalyScore":
              plt.ylim(-0.2, 1.2)
      
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