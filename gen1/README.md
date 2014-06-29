# NuPIC Critic

<table>
<tr>
  <td>
    <img src="https://github.com/numenta/nupic/wiki/images/icons/warning.png"/>
  </td>
  <td>
    <h3>This DEMO sortof works</h3>
    <p>I created it at the 2014 NuPIC Spring Hackathon, but didn't get it working properly. I figured out what the problem was and updated the code so that data is input into NuPIC properly, but the results are less than impressive. Currently experimenting with different ways to process audio wav data so that NuPIC understands it better.</p>
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

    ./run.py path/to/input_data.csv [--plot]

This will create a NuPIC model with the model params created by the previous swarm and feed the input data specified into it. Use the input file created by `generate_data.py`. If the `--plot` option is specified, will plot the actual and predicted values for the specified frequency bucket instead of writing output data. This is useful for debugging. 

### Plotting the results

    ./plotter.py path/to/output_data.csv [path/to/audio.wav]

Use the output file created by `run.py`. If the path to an wav file is given, will attempt to open the wave file with system `open` command and play it synced with the plot. 
