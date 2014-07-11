Get anomalies from audio input in 3 easy steps!

![NuPIC Critic plot screenshot](http://i.imgur.com/QzWQion.png)

### 1. Generate NuPIC Input From WAV

    ./convert_wav.py <path/to/wav>

There are several options for this, which you can see with the `--help` flag. You can control the FFT histogram sample rate, the number of histogram buckets, and the output directory where the file is written.

The resulting folder contains files formatted for NuPIC model input.

### 2. Run NuPIC

    ./run.py <path/to/input/directory> [options]
    
Runs all the prepared data in the input directory. Expects this directory to have been created by the `convert_wav.py` script above.

### 3. Plot the Results

    ./plotter.py <path/to/nupic/output/directory> [options]
    
Plots the results. Use `--wav` to pass in a WAV file to play at the same time (**CURRENTLY OUT OF SERVICE**).  There are several options for this, which you can see with the `--help` flag. 
