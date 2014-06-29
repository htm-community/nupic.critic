import numpy as N
import wave

class SoundFile:
   def  __init__(self, signal):
       self.file = wave.open('test.wav', 'wb')
       self.signal = signal
       self.sr = 44100

   def write(self):
       self.file.setparams((1, 2, self.sr, 44100*4, 'NONE', 'noncompressed'))
       self.file.writeframes(self.signal)
       self.file.close()

# let's prepare signal
duration = 4 # seconds
samplerate = 44100 # Hz
samples = duration*samplerate
frequency = 340 # Hz
period = samplerate / float(frequency) # in sample points
omega = N.pi * 2 / period

xaxis = N.arange(int(period),dtype = N.float) * omega
print xaxis
ydata = 16384 * N.sin(xaxis)
print ydata

signal = N.resize(ydata, (samples,))
print signal
ssignal = ''
for i in range(len(signal)):
   ssignal += wave.struct.pack('h',signal[i]) # transform to binary

f = SoundFile(ssignal)
f.write()
print 'file written'