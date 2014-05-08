# NuPIC Critic

<table>
<tr>
  <td>
    <img src="https://github.com/numenta/nupic/wiki/images/icons/warning.png"/>
  </td>
  <td>
    <h3>This DEMO doesn't really work yet</h3>
    <p>I created it at the 2014 NuPIC Spring Hackathon, but didn't get it working properly. I'll find some time to work on this, but for now I'm pushing to Github in case others want to see it and try to fix it.</p>
  </td>
</tr>
</table>

### Generating data from WAV files

    ./generate_data.py path/to/file.wav [--plot]

This will generate a NuPIC input data file in the `data` directory for the wav file. It performs a FFT using `matplotlib`'s `specgram` functionality. Then it creates a histogram for each sample over the frequency space with 10 buckets. This is the data written to the NuPIC input file.

If you specify `--plot`, the spectrogram of the FFT data will be displayed instead of the output file written.

### Swarming over the input data

    ./swarm.py path/to/input_data.csv

Use the input file created by `generate_data.py`. This swarm will take quite a long time, because the input data file has 10 fields to swarm over. The swarm is targeting bucket 3, but there's really no reason for that.

### Running the data through NuPIC

    ./run.py path/to/input_data.csv

This will create a NuPIC model with the model params created by the previous swarm and feed the input data specified into it. Use the input file created by `generate_data.py`.

### Plotting the results

    ./plotter.py path/to/output_data.csv [path/to/audio.wav]

Use the output file created by `run.py`. If the path to an wav file is given, will attempt to open the wave file and play it synced with the plot. 
