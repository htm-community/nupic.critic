## Requirements

- [matplotlib](http://matplotlib.org/)
- [numpy](http://www.numpy.org/)

Get anomalies from audio input in 3 easy steps!

![NuPIC Critic plot screenshot](http://i.imgur.com/QzWQion.png)

### 1. Generate NuPIC Input From WAV

    ./convert_wav.py <path/to/wav>

There are several options for this, which you can see with the `--help` flag. You can control the FFT histogram sample rate, the number of histogram buckets, and the output directory where the file is written.

The resulting folder contains files formatted for NuPIC model input.

#### Options

- `--buckets,-b`: _[default 10]_ Number of frequency buckets to split the input when applying the FFT.
- `--sample-rate,-s`: _[default 5]_ How many samples to take per second.
- `--output_directory,-o`: _[default "output"]_ Directory to write the NuPIC input files.
- `--verbose,-v`: _[default `False`]_ Print debugging statements.

### 2. Run NuPIC

    ./run.py <path/to/input/directory> [options]
    
Runs all the prepared data in the input directory. Expects this directory to have been created by the `convert_wav.py` script above.

- `--model_params,-m`: _[default "1field_anomaly"]_ Name of the model params to use (without the '_model_params.py'). You won't need to set this unless you really know what you are doing.
- `--plot,-p`: _[default `False`]_ Plots the output instead of writing to file.
- `--verbose,-v`: _[default `False`]_ Print debugging statements.

### 3. Plot the Results

    ./plotter.py <path/to/nupic/output/directory> [options]
    
Plots the results. Use `--wav` to pass in a WAV file to play at the same time (**CURRENTLY OUT OF SERVICE**).  There are several options for this, which you can see with the `--help` flag. 

- `--wav,-w`: _[default `None`]_ OUT OF SERVICE! Path to a WAV file to play synced to the plot.
- `--maximize,-m`: _[default `False`]_ Maximize plot window.
