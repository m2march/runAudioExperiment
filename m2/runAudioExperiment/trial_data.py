import os
import random
from m2.runAudioExperiment import audio

TRIAL_SETTINGS_FILENAME = 'trial_settings.csv'

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
        self.c1_data = audio.separator_sound_data(this.c1_duration)
        self.c2_data = audio.separator_sound_data(this.c2_duration)
        self.stimulus_w_silence_data = audio.extend_stimulus_w_silence(
            self.stimulus_path, self.silence_duration)

    def execute(self, env):
        # Black square 
        init_time = env.clock.getTime()
        env.black_rect.draw()
        env.win.flip()
        # TODO: Record elapsed time or set durations as multiples
        # of frame durations
        while env.clock.getTime() - init_time < self.black_duration:
            win.flip()
        # Cleaning 1
        env.c1_duration.draw()
        env.win.flip()
        sounddevice.play(self.c1_data.data, samplerate=self.c1_data.sr,
                         blocking=True)
        # Stimuli presentation
        env.black_rect.draw()
        env.win.flip()
        sr = self.stimulus_w_silence_data.sr
        rec_data = sounddevice.playrec(self.stimulus_w_silence_data.data,
                                       samplerate=sr, blocking=True)
        self.recording = audio.AudioData(rec_data, sr)
        # Cleaning 2
        env.c2_duration.draw()
        env.win.flip()
        sounddevice.play(self.c2_data.data, samplerate=self.c2_data.sr,
                         blocking=True)

    def save(self):
        wavfile.write(self.recording_path, self.recording.sr,
                      self.recording.data)


class TrialsData(list):
    'Stores information for each trial'

    def __init__(self, experiment_config):
        super().__init__([
            SingleTrialData(experiment_config, stimulus_path)
            for stimuli_path in experiment_config.stimuli_list
        ])

        self.config = experiment_config

    def save(self):
        trial_settings = pd.DataFrame.from_records([
            {
                'index': idx,
                'stimulus_path': self.stimulus_path,
                'recording_path': self.recording_path,
                'black_duration': self.black_duration,
                'silence_duration': self.silence_duration,
                'c1_duration': self.c1_duration,
                'c2_duration': self.c2_duration
            }
            for idx, std in enumerate(self)
        ])
        trial_settings_path = os.path.join(self.config.output_dir,
                                           TRIAL_SETTINGS_FILENAME)
        trial_settings.to_csv(trial_settings_path, index=False)

        for std in self:
            std.save(self.config.output_dir)
