import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt

rate, data = wavfile.read('../resources/Santana.wav')
print len(data)
time = np.arange(len(data))*1.0/rate

plt.plot(time, data)
plt.show()