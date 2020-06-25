import os
import random
import logging
import time
import sounddevice
import pandas as pd
from scipy.io import wavfile
from m2.runAudioExperiment import audio

TRIAL_SETTINGS_FILENAME = 'trial_settings.csv'
TRIAL_DURATIONS_FILENAME = 'trial_durations.csv'

logger = logging.getLogger('m2.runAudioExperiment.trials')

class SingleTrialData:
    'Stores information for a trial. Allows preparation and execution.'

    @staticmethod
    def recording_filename(stimulus_path):
        basename = os.path.basename(stimulus_path)
        prefix, ext = os.path.splitext(basename) 
        return '{}.rec{}'.format(prefix, ext)

    @staticmethod
    def create_duration(duration_cfg):
        if isinstance(duration_cfg, list) or isinstance(duration_cfg, tuple):
            return random.uniform(duration_cfg[0], duration_cfg[1])
        else:
            return duration_cfg

    def __init__(self, stimulus_path, experiment_config):
        self.stimulus_path = stimulus_path
        self.recording_path = os.path.join(
            experiment_config.output_dir,
            self.recording_filename(stimulus_path)
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
        self.c1_data = audio.create_separator_sound_data(self.c1_duration)
        self.c2_data = audio.create_separator_sound_data(self.c2_duration)
        self.stimulus_w_silence_data = audio.extend_stimulus_w_silence(
            self.stimulus_path, self.silence_duration)

    def execute(self, env):
        self.execution_times = {}
        # Black square 
        init_time = env.clock.getTime()
        win = env.window
        logger.debug('Black rect start: {}'.format(time.time()))
        env.black_rect.draw()
        win.flip()
        black_rect_start_time = env.clock.getTime()
        # TODO: Record elapsed time or set durations as multiples
        # of frame durations
        while env.clock.getTime() - init_time < self.black_duration / 1000:
            win.flip()
        # Cleaning 1
        if (self.c1_data is None):
            logger.debug('C1 skipped: {}'.format(time.time()))
            c1_start_time = env.clock.getTime()
        else:
            logger.debug('C1 start: {}'.format(time.time()))
            env.c1_rect.draw()
            win.flip()
            c1_start_time = env.clock.getTime()
            sounddevice.play(self.c1_data.data, samplerate=self.c1_data.sr,
                             blocking=True)

        self.execution_times['black_duration'] = (c1_start_time -
                                                  black_rect_start_time)
        
        # Stimuli presentation
        sr = self.stimulus_w_silence_data.sr
        logger.debug('Stimulus start (sr={}): {}'.format(sr, time.time()))
        env.black_rect.draw()
        win.flip()
        stimulus_start_time = env.clock.getTime()
        self.execution_times['c1_duration'] = (stimulus_start_time - 
                                          c1_start_time)
        rec_data = sounddevice.playrec(self.stimulus_w_silence_data.data,
                                       samplerate=sr, blocking=True,
                                       channels=2
                                      )
        self.recording = audio.AudioData(rec_data, sr)
        # Cleaning 2
        if (self.c2_data is None):
            logger.debug('C2 skipped: {}'.format(time.time()))
            c2_start_time = env.clock.getTime()
        else:
            logger.debug('C2 start: {}'.format(time.time()))
            env.c2_rect.draw()
            win.flip()
            c2_start_time = env.clock.getTime()
            sounddevice.play(self.c2_data.data, samplerate=self.c2_data.sr,
                             blocking=True)
        
        self.execution_times['stimulus_duration'] = (c2_start_time -
                                                     stimulus_start_time)
        c2_end_time = env.clock.getTime()
        self.execution_times['c2_duration'] = (c2_end_time - c2_start_time)

    def save(self):
        wavfile.write(self.recording_path, self.recording.sr,
                      self.recording.data)


class TrialsData(list):
    'Stores information for each trial'

    def __init__(self, experiment_config):
        super().__init__([
            SingleTrialData(stimulus_path, experiment_config)
            for stimulus_path in experiment_config.stimuli_list
        ])

        self.config = experiment_config

    def save(self):
        trial_settings = pd.DataFrame.from_records([
            {
                'index': idx,
                'stimulus_path': std.stimulus_path,
                'recording_path': std.recording_path,
                'black_duration': std.black_duration,
                'silence_duration': std.silence_duration,
                'c1_duration': std.c1_duration,
                'c2_duration': std.c2_duration
            }
            for idx, std in enumerate(self)
        ])
        trial_settings_path = os.path.join(self.config.output_dir,
                                           TRIAL_SETTINGS_FILENAME)
        trial_settings.to_csv(trial_settings_path, index=False)

        for std in self:
            std.save()

        if (self.config.duration_debug):
            trial_durations = pd.DataFrame.from_records([
                std.execution_times
                for idx, std in enumerate(self)
            ])
            trial_durations = trial_durations * 1000
            trial_durations_path = os.path.join(self.config.output_dir,
                                                TRIAL_DURATIONS_FILENAME)
            trial_durations.to_csv(trial_durations_path, index=False)
