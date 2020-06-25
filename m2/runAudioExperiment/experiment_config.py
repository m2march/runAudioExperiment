import yaml
import os
import typing
import logging
from fuzzywuzzy import fuzz
import sounddevice
import json


SOUND_DEVICE_THRESHOLD = 80
BEST_DEVICE_MATCH_THRESHOLD = 10
EXPERIMENT_SETTINGS_FILENAME = 'experiment_settings.json'

LOGGER = logging.getLogger('m2.runAudioExperiment.experment_config')

class ExperimentConfigError(ValueError):
    pass


class IncompleteExperimentConfig(ExperimentConfigError):
    
    def __init__(self, missing_keys, filename):
        self.missing_keys = missing_keys
        self.filename = filename
        super().__init__('Experiment config loaded from {} is missing the '
                         'following keys: {}'.format(filename, missing_keys))


class InvalidConfigType(ExperimentConfigError):

    def __init__(self, key, type, filename):
        self.key = key
        self.type = type
        self.filename = filename
        super().__init__('Experiment config has illegal type for variable '
                         '"{}" in file {}. Expected {}'.format(
                             key, filename, type))


class MissingStimuliFiles(ExperimentConfigError):

    def __init__(self, missing):
        self.missing = missing
        super().__init__(
            'The following stimuli files could not be found: {}'.format(
                self.missing))


class IllegalOutputDirectory(ExperimentConfigError):

    def __init__(self, output_dir):
        self.output_dir = output_dir
        super().__init__(
            'The following output directory is not empty: {}'.format(
                self.output_dir))


class NoMatchingDeviceFound(ExperimentConfigError):

    def __init__(self, sound_device, ratios):
        self.ratios = ratios
        super().__init__(
            ('No matching sound device found for name: {}\n'
             'Options are: {}').format(
                 sound_device,
                 [x['info']['name'] for x in ratios]
             )
        )


def check_type(instance, type):
    if isinstance(type, typing._GenericAlias):
        if (type.__origin__ == typing.Union):
            return any(check_type(instance, st) for st in type.__args__)
        elif (type.__origin__ == tuple):
            if isinstance(instance, tuple):
                return all([check_type(x, st)
                            for x, st in zip(instance, type.__args__)])
    else:
        return isinstance(instance, type)
    return False


class ExperimentRunConfig:
    
    config_keys = {
        'black_duration': typing.Union[int, typing.Tuple[int, int]],
        'c1_duration': typing.Union[int, typing.Tuple[int, int]],
        'c1_color': str,
        'c2_duration': typing.Union[int, typing.Tuple[int, int]],
        'c2_color': str,
        'randomize': bool,
        'sound_device': str,
        'silence_duration': typing.Union[int, typing.Tuple[int, int]]
    }
    config_keys_set = set(config_keys.keys())

    def __init__(self, file, stimuli_list, output_dir, duration_debug=False):
        if isinstance(file, str):
            with open(file, 'r') as f:
                config = yaml.load(f, Loader=yaml.Loader)
        else:
            config = yaml.load(file, Loader=yaml.Loader)
    
        if not self.config_keys_set.issubset(set(config.keys())):
            raise IncompleteExperimentConfig(
                self.config_keys_set - set(config.keys()), filename)

        for k, t in self.config_keys.items():
            if not check_type(config[k], t):
                raise InvalidConfigType(k, t, filename)

            self.__dict__[k] = config[k]


        if isinstance(stimuli_list, str):
            with open(stimuli_list, 'r') as f:
                self.stimuli_list = [l.strip() for l in f.readlines()]
        else:
            self.stimuli_list = [l.strip() for l in stimuli_list.readlines()]

        files_not_found = [x for x in self.stimuli_list
                           if not os.path.isfile(x)]

        if len(files_not_found) > 0:
            raise MissingStimuliFiles(files_not_found)

        if os.path.isdir(output_dir):
            if len(os.listdir(output_dir)) > 0:
                raise IllegalOutputDirectory(output_dir)
        else:
            LOGGER.info('Creating output dir: {}'.format(output_dir))
            os.mkdir(output_dir)
        self.output_dir = output_dir

        self.device_info, self.device_id = self.find_sound_device(
            self.sound_device)

        self.duration_debug = duration_debug

    def find_sound_device(self, sound_device):
        devices = sounddevice.query_devices()
        ratios = [{'id': i, 'info': info, 
                   'ratio': fuzz.partial_ratio(info['name'], sound_device)}
                  for i, info in enumerate(devices)]

        if all([x['ratio'] < SOUND_DEVICE_THRESHOLD for x in ratios]):
            raise NoMatchingDeviceFound(sound_device, ratios)
        
        sorted_ratios = sorted(ratios, key=lambda d: d['ratio'])
        best = sorted_ratios[-1]

        #TODO: Assert matching string is distinctive enough
        # distances = [best['ratio'] - x['ratio'] 
        #              for x in sorted_ratios[:-1]]
        # close_distances = [
        #     x for x in sorted_ratios[:-1]
        #     if best['ratio'] - x['ratio'] < BEST_DEVICE_MATCH_THRESHOLD
        # ]
        # if len(close_distances) > 0:
        #     raise MatchingNotDistinctEnough(best, close_distances)

        return best['info'], best['id']

    def save(self):
        out_path = os.path.join(self.output_dir, EXPERIMENT_SETTINGS_FILENAME)
        with open(out_path, 'w') as f:
            json.dump(self.__dict__, f)
