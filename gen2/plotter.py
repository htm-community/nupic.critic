#!/usr/bin/env python
import sys
import os
import csv
from optparse import OptionParser
import matplotlib
matplotlib.use('TKAgg')
from plot_output import NuPICPlotOutput

WINDOW = 200
HIGHLIGHT_ALPHA = 0.3
ANOMALY_HIGHLIGHT_COLOR = 'red'
ANOMALY_THRESHOLD = 0.9


parser = OptionParser(
  usage="%prog <path/to/nupic/output/directory> [options]\n\nPlot nupic "
        "output, optionally syncing the output to the playing of the original WAV file."
)

parser.add_option(
  "-w",
  "--wav",
  dest="wav",
  default=None,
  # FIXME: audio option doesn't work.
  help="OUT OF SERVICE! Path to a WAV file to play synced to the plot.")
parser.add_option(
  "-m",
  "--maximize",
  action="store_true",
  default=False,
  dest="maximize",
  help="Maximize plot window."
)



def highlightChart(old_highlights, new_highlights, chart):
  for highlight in new_highlights:
    # Each highlight contains [start-index, stop-index, color, alpha]
    old_highlights.append(chart.axvspan(
      highlight[0], highlight[1],
      color=highlight[2], alpha=highlight[3]
    ))



def extractAnomalyIndices(anomalyLikelihood):
  anomaliesOut = []
  anomalyStart = None
  for i, likelihood in enumerate(anomalyLikelihood):
    if likelihood >= ANOMALY_THRESHOLD:
      if anomalyStart is None:
        # Mark start of anomaly
        anomalyStart = i
    else:
      if anomalyStart is not None:
        # Mark end of anomaly
        anomaliesOut.append((
          anomalyStart, i, ANOMALY_HIGHLIGHT_COLOR, HIGHLIGHT_ALPHA
        ))
        anomalyStart = None

  # Cap it off if we're still in the middle of an anomaly
  if anomalyStart is not None:
    anomaliesOut.append((
      anomalyStart, len(anomalyLikelihood)-1,
      ANOMALY_HIGHLIGHT_COLOR, HIGHLIGHT_ALPHA
    ))
  print anomaliesOut
  return anomaliesOut



def run(input_dir, audio_file, maximize):
  file_names = os.listdir(input_dir)
  bins = [os.path.splitext(n)[0] for n in file_names]
  input_files = [open(os.path.join(input_dir, f)) for f in file_names]

  readers = [csv.reader(f) for f in input_files]

  headers = [reader.next() for reader in readers]
  for reader in readers:
    reader.next()
    reader.next()

  output = NuPICPlotOutput(input_dir, bins, maximize)

  while True:
    try:
      next_lines = [reader.next() for reader in readers]
    except StopIteration:
      break

    seconds = next_lines[0][headers[0].index("seconds")]
    bin_values = []
    anomaly_likelihoods = []

    for i, line in enumerate(next_lines):
      bin = bins[i]
      header = headers[i]
      bin_value = line[header.index(bin)]
      anomaly_likelihood = line[header.index("anomalyLikelihood")]
      bin_values.append(bin_value)
      anomaly_likelihoods.append(anomaly_likelihood)

    output.write(seconds, bin_values, anomaly_likelihoods)

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

  run(input_dir, audio_file, options.maximize)
