### Generate NuPIC Input From WAV

    ./convert_wav.py <path/to/wav>

There are several options for this, which you can see with the `--help` flag. You can control the FFT histogram sample rate, the number of histogram buckets, and the output directory where the file is written.

The resulting file is formatted for a swarm or NuPIC model input.

### Swarm Over NuPIC Input File

    ./swarm.py <path/to/input> [options]
    
There are also a bunch of swarm options you can specify on the command line, which you can see with the `--help` flag.

This produces a model parameter file in the `model_params` directory, which is created if you don't have one already.

