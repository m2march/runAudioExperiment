# Run Audio Experiment

`runAudioExperiment` is an utility to run an experimental setup where input
times must be recorded with precision synchronized to an audio stimulus. The 
utility was developed in the context of _"Simple and cheap setup for measuring 
timed responses to auditory stimuli"_ (Miguel et. al., under review).

The utility works by executing several trials that consist of reproducing an
auditory stimulus while simultaneously recording the signal of an input device.
As an output, the utility saves an audio file for each trial. With the expected
setup, each audio file has the input signal in one channel and the stimulus
signal in another. Recording both signals (the input and the stimulus loopback)
allows extracting the input times relative to the stimulus signal by
synchronizing the recording with the orignal stimulus (see utility
[`rec2taps`](https://github.com/m2march/rec2taps)).

For details on how to create the setup, please see Miguel et. al., under review.


## Installation

* From pypi:

```
    pip install m2-runAudioExperiment
```

* From sources:

```
    git clone https://github.com/m2march/runAudioExperiment.git
    cd runAudioExperiment
    python setup.py install
```

Once installation is done, the script `runAudioExperiment` should be available
in the command line interface.


# Usage

    runAudioExperiment trial_config stimuli_list output_dir

* `trial_config` is a path to a yaml format file describing the configuration
    of the execution
* `stimuli_list` is a path to a txt file declaring the path to the stimuli
    audios, one per line, relative to the current dir
* `output_dir` is a path to a directory where output from the experiment
    will be written. In case the directory does not exists, it will be created.
    If the directory exists, it must be empty.


## Trials

Each trial execution consists of the following steps:

* A black screen is shown for a specified duration
* Screen changes color and white noise with a tone is played
* A black screen is shown and the stimulus is played while recording the
  input device. A silence time after the stimulus ended can be configured.
* Screen changes color and white noise with a tone is played

Trials are executed back to back. 


## Configuration

The following is an example of a trial configuration file:

    black_duration: 600         # Duration of black screen (in ms)
    c1_duration: [1500, 3000]   # Duration of first noise screen (in ms)
    c1_color: "#afd444"         # Color of first noise screen
    c2_duration: 000            # Duration of second noise screen (in ms)
    c2_color: "#afd444"         # Color of second noise screen
    randomize: false            # Whether trial order should be randomized
    sound_device: "USB Audio"   # String or int identifying the sound deviced used
    silence_duration: 1500      # Duration of silence after stimuli playback

Durations may be specified as a single number or as a list of two numbers. If
it is a single number, it specifies the duration of the section. Otherwise, the
duration will be a random number between the two defined ones. If the duration
is 0, the section is skipped.

`sound_device` is a string used to locate the sound device to be used. In our
proposed setup, an external USB card is usted. A list of available devices
can be obtained by executing:

    `runAudioExperiment -l`


## Output

After the experiment is executed, the following files are generated in
`output_dir`:

* `experiment_settings.json`: a copy of the configuration defined in
    `trial_config` in json format. The configuration is extended with the
    complete information of the selected sound device.
* `trial_settings.csv`: a csv formatted table describing the executed trials.
    This table allows knowing the duration of the sections where duration was
    specified as an interval. It also presents the order in which the stimulus
    were presented in case the `randomize` setting was set to `true`.
* `*.rec.*`: a serie of audio files are generated, one per trial, with the
    recording of the input signal and the stimulus lookback. The files are
    prefixed with the basename of the stimulus file and end with a `.rec`
    extension continued with the original extension of the stimulus file.


### Example execution

The directory `example` contains example data to test run the utility and see
its workings and results. A test run can be done as so:

    $> cd example
    $> runAudioExperiment test_config.yaml stimuli_3.txt output

This will run the experiment with three stimuli and create a new folder named
`output` were recordings and `trial_settings.csv` will be output. 

Before using the utility it may be necessary to configure the `sound_device`
configuration in `test_config.yaml` to refer to a sound card available in the
computer. Use `runAudioExperiment -l` to list options.

### Caveat in the duration of the sections

The duration of the sections may differ slightly from the specifications,
mainly due to the delay in starting playback in the soundcard. Added delay is
around 20ms. The `--debug-durations` flag instructs the utility to write ohe
actual duration of the sections in an extra `trial_durtions.csv` file.
