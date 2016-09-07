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
from optparse import OptionParser
import numpy as np
import wave
import csv
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from scipy.io import wavfile


DEFAULT_BUCKETS = 10
DEFAULT_HISTOGRAMS_PER_SECOND = 5
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
  "--histograms_per_second",
  dest="histograms_per_second",
  default=DEFAULT_HISTOGRAMS_PER_SECOND,
  help="How many time per second to generate a frequency histogram.")
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
parser.add_option(
  "-p",
  "--plot",
  action="store_true",
  default=False,
  dest="plot",
  help="Plot WAV spectrogram in matplotlib instead of writing NuPIC input files.")
parser.add_option(
  "-l",
  "--loop",
  dest="loop_times",
  default=1,
  help="How many times to loop the WAV file (for reinforcing a pattern in "
       "NuPIC while training)."
)


def read_wav_data(wave_path, loop_times):
  print "Opening %s" % wave_path
  
  # Get wave parameters
  spf = wave.open(wave_path, "r")
  
  channels = spf.getnchannels()
  
  if channels > 2:
    raise ValueError("Can't process files with more than two channels.")
  
  sample_width = spf.getsampwidth()
  audio_sample_rate = spf.getframerate()
  num_frames = spf.getnframes()
  spf.close()
  
  # Get the wave file data
  signal = wavfile.read(wave_path)[1]
  if channels == 2:
    signal = signal.astype(float)
    signal = signal.sum(axis=1) / 2.0
      
  signal = signal.astype(np.int16)

  if loop_times > 1:
    if verbose:
      print "Looping WAV onto itself %i times..." % loop_times
    looped_signal = np.copy(signal)
    for i in xrange(1, loop_times):
      looped_signal = np.append(looped_signal, signal)
    signal = looped_signal


  signal_length = len(signal)
  # Total seconds length of the wave file.
  seconds = signal_length / audio_sample_rate


  if verbose:
    print "Sample width (bytes): %i" % sample_width
    print "Frame rate (sampling frequency): %i" % audio_sample_rate
    print "Number of frames: %i" % num_frames
    print "Signal length: %i" % signal_length
    print "Seconds: %i" % seconds

  return (sample_width, audio_sample_rate, signal_length, seconds, signal)



def get_fft_histogram(signal, audio_sample_rate, seconds, histograms_per_second, buckets, plot):
  window_size = audio_sample_rate / histograms_per_second
  overlap_ratio = 0.0

  # FFT the signal and extract frequency components
  # Some parameter explanations:
  #   NFFT = the number of samples grouped into each specgram
  #   Fs = The sample rate of the signal
  specgram = mlab.specgram(
    signal,
    NFFT=window_size,
    Fs=audio_sample_rate,
    window=mlab.window_hanning,
    noverlap=int(window_size * overlap_ratio))

  # The periodogram is a 2D array in the format: [frequencyId][sampleId]
  # The actual frequency of each {frequencyId} is recorded in specgram[1]
  #   where specgram[1][frequencyId] will return the frequency value in Hz
  # The {sampleId} represents the sample number after the total number of
  #   samples is grouped by {window_size}
  # Each data point in this array represents signal density at a particular
  #   frequency and sample number
  periodogram = specgram[0]

  if verbose:
    print "Dimensions of periodogram: %i x %i" % (len(periodogram), len(periodogram[0]))

  # apply log transform since specgram() returns linear array
  # volume is logrithmic, therefore the periodogram's data (which represents 
  #   amplitude / density of each frequency) must be converted
  arr2D = 10 * np.log10(periodogram)
  arr2D[arr2D == -np.inf] = 0  # replace infs with zeros
  arr2D[arr2D < 0] = 0  # replace negatives with zeros

  if plot:
    fig = plt.figure(figsize=(6, 3.2))
    ax = fig.add_subplot(111)
    ax.set_title('Spectrogram')
    plt.imshow(arr2D)
    ax.set_aspect('equal')
    plt.colorbar(orientation='vertical')
    plt.show()
    return None

  else:
    # Converts periodogram from format [frequencyId][sampleId]
    #   to [sampleId][frequencyId]
    flipped = np.transpose(arr2D)

    if verbose:
      print "Total samples: %i" % len(flipped)
      print "Samples per second: %f" % (len(flipped) / seconds)
      print "Grouping FFT into %i-bucket histogram..." % buckets

    grouped = []
    # Each row of flipped is already effectively a histogram of the frequencies,
    #    where each bucket is a single frequency
    # Groups the entire frequency range
    #   into {buckets} number of buckets of summed amplitudes 
    #   of all the frequencies in the bucket
    _,num_frequencies = flipped.shape
    step = num_frequencies // buckets
    for i, sample in enumerate(flipped):
      perc_done = float(i+1) / len(flipped)
      elapsed_seconds = (perc_done * seconds)
      histogram = []
      left_freq = 0
      for bin_num in range(buckets):
        right_freq = min(left_freq + step, num_frequencies - 1)
        # Sum the amplitudes of the frequencies in the range left_freq to right_freq
        bin_value = int(sum(sample[left_freq:right_freq]))
        histogram.append(bin_value)
        left_freq = right_freq
        
      histogram = [elapsed_seconds] + histogram
      grouped.append(histogram)

    return grouped



def writeCsvs(data, out_path):
  if not os.path.exists(out_path):
    os.makedirs(out_path)
  bins = [("b%i" % i) for i in xrange(len(data[0]) - 1)]
  for bin in bins:
    output_file_name = os.path.join(out_path, "%s.csv" % bin)
    with open(output_file_name, "wb") as out_file:
      writer = csv.writer(out_file)
      headers = ["seconds", bin]
      types = ["float", "int"]
      flags = ["",""]
      writer.writerow(headers)
      writer.writerow(types)
      writer.writerow(flags)
      for line in data:
        writer.writerow([line[0], line[1 + bins.index(bin)]])

  print "Wrote data to %s" % out_path



def run(buckets, histograms_per_second, wav_path, loop_times, plot, data_dir):
  sample_width, audio_sample_rate, signal_length, seconds, signal \
    = read_wav_data(wav_path, loop_times)
  histogram = get_fft_histogram(
    signal, audio_sample_rate, seconds, histograms_per_second, buckets, plot
  )
  if histogram:
    wav_in_name = os.path.splitext(os.path.basename(wav_path))[0]
    output_name = "%s_%ihz_%ib" % (wav_in_name, histograms_per_second, buckets)
    if not os.path.exists(data_dir):
      os.makedirs(data_dir)
    output_dir = os.path.join(output_name, "input")
    writeCsvs(histogram, os.path.join(data_dir, output_dir))


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
    int(options.histograms_per_second),
    wav_path,
    int(options.loop_times),
    options.plot,
    options.output_dir
  )
