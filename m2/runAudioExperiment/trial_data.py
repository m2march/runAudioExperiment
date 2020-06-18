import os
import random
from m2.runAudioExperiment import audio


class SingleTrialData:
    'Stores information for a trial. Allows preparation and execution.'

    @classmethod
    def recording_filename(stimulus_path):
        basename = os.path.basename(stimuli_path)
        prefix, ext = os.path.splitext(basename) 
        return '{}.rec.{}'.format(prefix, ext)

    @classmethod
    def create_duration(duration_cfg):
        if isinstance(duration_cfg, list) or isinstance(duration_cfg, tuple):
            return random.uniform(duration_cfg[0], duration_cfg[1])
        else:
            return duration_cfg

    def __init__(self, stimulus_path, experiment_config):
        self.stimulus_path = stimuli_path
        self.recording_path = os.path.join(
            experiment_config.output_dir,
            this.recording_filename(stimulus_path)
        )
        self.black_duration = self.create_duration(
            experiment_config.black_duration)
        self.silence_duration = self.create_duration(
            experiment_config.silence_duration)
        # TODO: Set durations as multiples of frame duration
        self.c1_duration = self.create_duration(
            experiment_config.c1_duration)
        self.c2_duration = self.create_duration(
            experiment_config.c2_duration)

    def prepare(self, env):
        '''
        Prepares the data required to execute the trial.

        This includes:
            * creating the initial separation audio data
            * creating the ending separation audio data
            * load stimuli's data and extend it with silence 
        '''
        self.c1_file = audio.separator_sound_data(this.c1_duration)
        self.c2_file = audio.separator_sound_data(this.c2_duration)
        self.stimulus_w_silence_path = audio.extend_stimulus_w_silence(
            self.stimulus_path, self.silence_duration)

    def execute(self, env):
        pass


class TrialsData(list):
    'Stores information for each trial'

    def __init__(self, experiment_config):
        super().__init__([
            SingleTrialData(experiment_config, stimulus_path)
            for stimuli_path in experiment_config.stimuli_list
        ])
