### Generate NuPIC Input From WAV

    ./convert_wav.py <path/to/wav>

There are several options for this, which you can see with the `--help` flag. You can control the FFT histogram sample rate, the number of histogram buckets, and the output directory where the file is written.

The resulting file is formatted for a swarm or NuPIC model input.

### Swarm Over NuPIC Input File

> **WARNING**: This step is deprecated, but I'm leaving the docs here for now because it still works. There are pre-canned anomaly model params now in the `model_params` directory.

    ./swarm.py <path/to/input> [options]
    
There are also a bunch of swarm options you can specify on the command line, which you can see with the `--help` flag.

This produces a model parameter file in the `model_params` directory, which is created if you don't have one already.

### Run NuPIC

    ./run.py <path/to/input/directory> [options]
    
Runs all the prepared data in the input directory. Expects this directory to have been created by the `convert_wav.py` script above.

### Plot the Results

    ./plotter.py <path/to/nupic/output/directory> [options]
    
Plots the results. Use `--wav` to pass in a WAV file to play at the same time.