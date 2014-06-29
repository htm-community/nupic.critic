# import scipy.io.wavfile as wavfile
# import scikits.audiolab
import numpy as np
import pylab as pl



# x, fs, nbits = audiolab.wavread('schubert.wav')
# audiolab.play(x, fs)
# N = 4*fs    # four seconds of audio
# X = scipy.fft(x[:N])
# Xdb = 20*scipy.log10(scipy.absolute(X))
# f = scipy.linspace(0, fs, N, endpoint=False)
# pylab.plot(f, Xdb)
# pylab.xlim(0, 5000)   # view up to 5 kHz

# rate, data = wavfile.read('../resources/Who2.wav')

# t = np.arange(len(data[:,0]))*1.0/rate
# pl.plot(t, data[:,0])
# pl.show()

# p = 20*np.log10(np.abs(np.fft.rfft(data[:2048, 0])))
# f = np.linspace(0, rate/2.0, len(p))
# pl.plot(f, p)
# pl.xlabel("Frequency(Hz)")
# pl.ylabel("Power(dB)")
# pl.show()

import matplotlib.pyplot as plt
import numpy as np
import wave
import sys



def run(wave_path):
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

# #Extract Raw Audio from Wav File
# signal = spf.readframes(100000)
# signal = np.fromstring(signal, 'Int16')
# fs = spf.getframerate()

# #If Stereo
# if spf.getnchannels() == 2:
#     print 'Just mono files'
#     sys.exit(0)

  time_slice = [20000, 40000]

  # Time=np.linspace(0, len(signal[time_slice[0]:time_slice[1]])/frame_rate, num=(time_slice[1] - time_slice[0]))
  Time=np.linspace(0, len(signal)/frame_rate, num=len(signal))

  plt.figure(1)
  plt.title('Signal Wave...')
  plt.plot(signal[20000:40000])
  plt.show()


if __name__ == "__main__":
  args = sys.argv[1:]
  input_path = args[0]
  run(input_path)