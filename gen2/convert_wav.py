#!/usr/bin/env python

import sys
import os
from optparse import OptionParser
import numpy as np
import wave
import csv
import matplotlib.mlab as mlab


DEFAULT_BUCKETS = 10
DEFAULT_SAMPLE_RATE = 5
DEFAULT_OUTPUT_DIR = "data"
verbose = False

parser = OptionParser(
  usage="%prog <path/to/wav> [options]\n\nConvert wav file into NuPIC input."
)

parser.add_option(
    "-b",
    "--buckets",
    dest="buckets",
    default=DEFAULT_BUCKETS,
    help="Number of frequency buckets to split the input when applying the "
         "FFT.")
parser.add_option(
    "-s",
    "--sample_rate",
    dest="sample_rate",
    default=DEFAULT_SAMPLE_RATE,
    help="How many samples to take per second.")
parser.add_option(
    "-o",
    "--output_directory",
    dest="output_dir",
    default=DEFAULT_OUTPUT_DIR,
    help="Directory to write the NuPIC input file.")
parser.add_option(
  "-v",
  "--verbose",
  action="store_true",
  default=False,
  dest="verbose",
  help="Print debugging statements.")


def read_wav_data(wave_path):
  print "Opening %s" % wave_path
  spf = wave.open(wave_path, "r")

  channels = spf.getnchannels()
  sample_width = spf.getsampwidth()
  frame_rate = spf.getframerate()
  num_frames = spf.getnframes()
  # Read in all frames.
  signal = spf.readframes(spf.getnframes()-1)
  spf.close()

  # Convert to numpy array.
  signal = np.fromstring(signal, 'Int16')
  signal_length = len(signal)
  # Total seconds length of the wave file.
  seconds = signal_length / frame_rate


  if channels > 1:
    raise ValueError("Can't process stereo files.")
  if verbose:
    print "Sample width (bytes): %i" % sample_width
    print "Frame rate (sampling frequency): %i" % frame_rate
    print "Number of frames: %i" % num_frames
    print "Signal length: %i" % signal_length
    print "Seconds: %i" % seconds

  return (sample_width, frame_rate, signal_length, seconds, signal)



def get_fft_histogram(signal, frame_rate, seconds, sample_rate, buckets):
  window_size = frame_rate / sample_rate
  overlap_ratio = 0.0

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

  flipped = np.transpose(arr2D)

  if verbose:
    print "Total samples: %i" % len(flipped)
    print "Samples per second: %f" % (len(flipped) / seconds)
    print "Grouping FFT into %i-bucket histogram..." % buckets

  grouped = []
  for i, sample in enumerate(flipped):
    perc_done = float(i+1) / len(flipped)
    elapsed_seconds = (perc_done * seconds)
    histogram = np.array(np.histogram(
      sample, bins=buckets)[0]
    ).tolist()
    histogram = [elapsed_seconds] + histogram
    grouped.append(histogram)

  return grouped



def writeCsv(data, out_path):
  with open(out_path, "wb") as out_file:
    writer = csv.writer(out_file)
    headers = ["seconds"] + [("b%i" % i) for i in xrange(len(data[0]) - 1)]
    types = ["float"] + ["int" for i in xrange(len(data[0]) - 1)]
    flags = ["" for i in xrange(len(data[0]))]
    writer.writerow(headers)
    writer.writerow(types)
    writer.writerow(flags)
    for line in data:
      writer.writerow(line)
  print "Wrote data to %s" % out_path



def run(buckets, sample_rate, wav_path, output_dir):
  sample_width, frame_rate, signal_length, seconds, signal \
    = read_wav_data(wav_path)
  histogram = get_fft_histogram(
    signal, frame_rate, seconds, sample_rate, buckets
  )
  wav_in_name = os.path.splitext(os.path.basename(wav_path))[0]
  output_name = "%s_%ihz_%ib_input.csv" % (wav_in_name, sample_rate, buckets)
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  writeCsv(histogram, os.path.join(output_dir, output_name))


if __name__ == "__main__":
  (options, args) = parser.parse_args(sys.argv[1:])
  try:
    wav_path = args.pop(0)
  except IndexError:
    parser.print_help(sys.stderr)
    sys.exit()

  verbose = options.verbose

  run(
    int(options.buckets),
    int(options.sample_rate),
    wav_path,
    options.output_dir
  )