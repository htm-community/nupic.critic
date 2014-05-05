#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from pydub import AudioSegment


DATA_DIR = "data"


def writeCsv(data, out_name):
  print "Writing data to %s" % out_name
  with open(out_name, "wb") as out_file:
    writer = csv.writer(out_file)
    headers = ["seconds"]
    headers = headers + [("b%i" % i) for i in xrange(len(data[0]) - 1)]
    types = ["float" for i in xrange(len(data[0]))]
    flags = ["" for i in xrange(len(data[0]))]
    writer.writerow(headers)
    writer.writerow(types)
    writer.writerow(flags)
    for line in data:
      writer.writerow(line)


def generate_data(input_path, plot):
  basename = os.path.basename(input_path)
  name = os.path.splitext(basename)[0]
  audiofile = AudioSegment.from_file(input_path)

  data = np.fromstring(audiofile._data, np.int16)

  channels = []
  for chn in xrange(audiofile.channels):
      channels.append(data[chn::audiofile.channels])

  channel = channels[0]
  audio_duration = audiofile.duration_seconds
  frame_rate = audiofile.frame_rate
  frame_count = audiofile.frame_count()
  print "Frame Rate: %s" % frame_rate
  print "Frame Count: %s" % frame_count
  print "Calculated Duration: %f" % (frame_count / frame_rate)
  window_size = 4096 * 4
  overlap_ratio = 0.5
  amp_min = 10

  # FFT the signal and extract frequency components
  arr2D = mlab.specgram(
      channel, # just one channel
      NFFT=window_size,
      Fs=frame_rate,
      window=mlab.window_hanning,
      noverlap=int(window_size * overlap_ratio))[0]

  # apply log transform since specgram() returns linear array
  arr2D = 10 * np.log10(arr2D)
  arr2D[arr2D == -np.inf] = 0  # replace infs with zeros

  if plot:
      fig = plt.figure(figsize=(6, 3.2))
      ax = fig.add_subplot(111)
      ax.set_title('Spectrogram')
      plt.imshow(arr2D)
      ax.set_aspect('equal')
      plt.colorbar(orientation='vertical')
      plt.show()
      exit()

  freq_min = np.amin(arr2D)
  freq_max = np.amax(arr2D)

  flipped = np.transpose(arr2D)

  print "Total samples: %i" % len(flipped)
  print "Samples per second: %f" % (len(flipped) / audio_duration)

  grouped = []
  for i, one in enumerate(flipped):
      # one = flipped[i]
      perc_done = float(i+1) / len(flipped)
      elapsed_seconds = (perc_done * audio_duration)
      histogram = np.array(np.histogram(one, range=(freq_min, freq_max))[0], dtype="float64")
      histogram = np.insert(histogram, 0, elapsed_seconds)
      grouped.append(histogram)

  writeCsv(grouped, "%s_input.csv" % (os.path.join(DATA_DIR, name)))


if __name__ == "__main__":
  args = sys.argv[1:]
  input_path = args[0]
  plot = False
  if "--plot" in args:
    plot = True
  generate_data(input_path, plot)
