import scipy
from scipy.io.wavfile import read
from scipy.signal import hann
from scipy.fftpack import rfft
import matplotlib.pyplot as plt

# read audio samples
input_data = read("../resources/Sleep.wav")
audio = input_data[1]
# apply a Hanning window
window = hann(1024)
audio = audio[:1024] * window
# fft
mags  = abs(rfft(audio))
# convert to dB
mags = 20 * scipy.log10(mags)
# normalize to 0 dB max
mags -= max(mags)

plt.plot(mags)
plt.ylabel("Magnitude (dB)")
plt.xlabel("Frequency Bin")
plt.title("Flute Spectrum")
plt.show()

# plot the first 1024 samples
# plt.plot(audio[0:1024])
# # label the axes
# plt.ylabel("Amplitude")
# plt.xlabel("Time (samples)")
# # set the title
# plt.title("Flute Sample")
# # display the plot
# plt.show()