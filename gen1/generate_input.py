#!/usr/bin/env python
import sys
import os
import csv
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import wave
# from pydub import AudioSegment


DATA_DIR = "data"
BUCKETS = 10
ISOLATE = "b3"


def writeCsv(data, out_name):
  print "Writing data to %s" % out_name
  with open(out_name, "wb") as out_file:
    writer = csv.writer(out_file)
    headers = ["seconds"] + [("b%i" % i) for i in xrange(len(data[0]) - 1)]
    types = ["float"] + ["int" for i in xrange(len(data[0]) - 1)]
    flags = ["" for i in xrange(len(data[0]))]
    writer.writerow(headers)
    writer.writerow(types)
    writer.writerow(flags)
    for line in data:
      writer.writerow(line)


def process_wave(wave_path):
  print "Opening %s" % wave_path
  spf = wave.open(wave_path, "r")

  channels = spf.getnchannels()
  sample_width = spf.getsampwidth()
  frame_rate = spf.getframerate()
  num_frames = spf.getnframes()
  # Read in all frames.
  signal = frames = spf.readframes(spf.getnframes()-1)
  # Read a few frames.
  # signal = spf.readframes(10)
  spf.close()

  # Convert to numpy array.
  signal = np.fromstring(signal, 'Int16')
  signal_length = len(signal)
  # Total seconds length of the wave file.
  seconds = signal_length / frame_rate

  print "%i channels" % channels
  if channels > 1:
    print "Can't process stereo files, sorry."
    sys.exit(0)
  print "Sample width (bytes): %i" % sample_width
  print "Frame rate (sampling frequency): %i" % frame_rate
  print "Number of frames: %i" % num_frames
  print "Signal length: %i" % signal_length
  print "Seconds: %i" % seconds

  return (sample_width, frame_rate, signal_length, seconds, signal)




def generate_data(input_path, plot):
  basename = os.path.basename(input_path)
  name = os.path.splitext(basename)[0]

  sample_width, frame_rate, signal_length, seconds, signal = process_wave(input_path)

  window_size = 4096 * 4
  overlap_ratio = 0.5
  amp_min = 10

  # FFT the signal and extract frequency components
  arr2D = mlab.specgram(
    signal,
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
  print "Samples per second: %f" % (len(flipped) / seconds)

  grouped = []
  for i, sample in enumerate(flipped):
    perc_done = float(i+1) / len(flipped)
    elapsed_seconds = (perc_done * seconds)
    histogram = np.array(np.histogram(
      sample, bins=BUCKETS)[0]
    ).tolist()
    histogram = [elapsed_seconds] + histogram
    grouped.append(histogram)

  writeCsv(grouped, "%s_input.csv" % (os.path.join(DATA_DIR, name)))


if __name__ == "__main__":
  args = sys.argv[1:]
  input_path = args[0]
  plot = False
  if "--plot" in args:
    plot = True
  generate_data(input_path, plot)
