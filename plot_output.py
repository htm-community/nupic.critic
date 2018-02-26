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
(This is a component of the One Hot Gym Anomaly Tutorial.)
"""
from collections import deque
import numpy as np
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

WINDOW = 300
HIGHLIGHT_ALPHA = 0.3
ANOMALY_HIGHLIGHT_COLOR = 'red'



def triggers_anomaly_threshold(data, anomaly_threshold, trigger_count):
  def above_threshold(value):
    return value >= anomaly_threshold
  breach_count = len(filter(above_threshold, data))
  return breach_count >= trigger_count



def extract_anomaly_indices(anomaly_likelihoods,
                            anomaly_threshold, anomaly_trigger_count):
  anomalies_out = []
  anomalyStart = None

  bin_values = np.transpose(anomaly_likelihoods.values())

  for i, likelihood_batch in enumerate(bin_values):
    likelihood_batch = [float(v) for v in bin_values[i]]
    if triggers_anomaly_threshold(likelihood_batch, anomaly_threshold, anomaly_trigger_count):
      if anomalyStart is None:
        # Mark start of anomaly
        anomalyStart = i
    else:
      if anomalyStart is not None:
        # Mark end of anomaly
        anomalies_out.append((
          anomalyStart, i, ANOMALY_HIGHLIGHT_COLOR, HIGHLIGHT_ALPHA
        ))
        anomalyStart = None

  # Cap it off if we're still in the middle of an anomaly
  if anomalyStart is not None:
    anomalies_out.append((
      anomalyStart, len(bin_values)-1,
      ANOMALY_HIGHLIGHT_COLOR, HIGHLIGHT_ALPHA
    ))
  return anomalies_out



class NuPICPlotOutput(object):


  def __init__(self, name, bins, maximize, anomaly_threshold, anomaly_trigger_count):
    self.name = name
    self.bins = bins
    self.anomaly_threshold = anomaly_threshold
    self.anomaly_trigger_count = anomaly_trigger_count
    # Turn matplotlib interactive mode on.
    plt.ion()
    self.seconds = []
    self.bin_values = {}
    self.anomaly_likelihoods = {}
    self.bin_lines = {}
    self.anomaly_likelihood_lines = {}
    self.lines_initialized = False
    self._chart_highlights = []
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 1, height_ratios=[3,  1])

    self._mainGraph = fig.add_subplot(gs[0, 0])
    plt.title(self.name)
    plt.xlabel('Seconds')

    self._anomalyGraph = fig.add_subplot(gs[1])

    plt.ylabel('Anomalies')
    plt.xlabel('Seconds')

    # Maximizes window
    if maximize:
      mng = plt.get_current_fig_manager()
      mng.resize(*mng.window.maxsize())

    plt.tight_layout()



  def initializeLines(self, seconds):
    print "initializing %s" % self.name
    anomalyRange = (-0.1, 1.1)
    self.seconds = deque([seconds] * WINDOW, maxlen=WINDOW)
    for freq_bin in self.bins:
      self.bin_values[freq_bin] = deque([0.0] * WINDOW, maxlen=WINDOW)

      self.anomaly_likelihoods[freq_bin] = deque([0.0] * WINDOW, maxlen=WINDOW)
      bin_plot, = self._mainGraph.plot(
        self.seconds, self.bin_values[freq_bin]
      )

      self.bin_lines[freq_bin] = bin_plot
      anomaly_plot, = self._anomalyGraph.plot(
        self.seconds, self.anomaly_likelihoods[freq_bin]
      )
      anomaly_plot.axes.set_ylim(anomalyRange)
      self.anomaly_likelihood_lines[freq_bin] = anomaly_plot

    self._mainGraph.legend(tuple(self.bins), loc=3)
    self._anomalyGraph.legend(
      tuple(sorted(self.anomaly_likelihood_lines.keys())), loc=3
    )
    self.lines_initialized = True



  def highlightChart(self, highlights, chart):
    for highlight in highlights:
      # Each highlight contains [start-index, stop-index, color, alpha]
      self._chart_highlights.append(chart.axvspan(
        self.seconds[highlight[0]], self.seconds[highlight[1]],
        color=highlight[2], alpha=highlight[3]
      ))



  def write(self, seconds, bin_values, anomaly_likelihoods):

    # We need the first timestamp to initialize the lines at the right X value,
    # so do that check first.
    if not self.lines_initialized:
      self.initializeLines(seconds)

    self.seconds.append(seconds)

    for i, freq_bin in enumerate(self.bins):
      self.bin_values[freq_bin].append(bin_values[i])
      self.anomaly_likelihoods[freq_bin].append(anomaly_likelihoods[i])

      # Update main chart data
      self.bin_lines[freq_bin].set_xdata(self.seconds)
      self.bin_lines[freq_bin].set_ydata(self.bin_values[freq_bin])
      self.anomaly_likelihood_lines[freq_bin].set_xdata(self.seconds)
      self.anomaly_likelihood_lines[freq_bin].set_ydata(self.anomaly_likelihoods[freq_bin])

    # Remove previous highlighted regions
    for poly in self._chart_highlights:
      poly.remove()
    self._chart_highlights = []

    # Highlight anomalies in anomaly chart
    anomalies = extract_anomaly_indices(self.anomaly_likelihoods,
                                        self.anomaly_threshold,
                                        self.anomaly_trigger_count)
    self.highlightChart(anomalies, self._anomalyGraph)

    # maxValue = max(self.allValues)
    # self._mainGraph.relim()
    # self._mainGraph.axes.set_ylim(0, maxValue + (maxValue * 0.02))

    self._mainGraph.relim()
    self._mainGraph.autoscale_view(True, True, True)
    self._anomalyGraph.relim()
    self._anomalyGraph.autoscale_view(True, True, True)

    plt.pause(0.000001) # This also calls draw()



  def close(self):
    plt.ioff()
    plt.show()
