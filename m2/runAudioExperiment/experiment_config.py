import yaml
import typing

class ExperimentConfigError(ValueError):
    pass

class IncompleteExperimentConfig(ExperimentRunConfig):
    
    def __init__(self, missing_keys, filename):
        self.missing_keys = missing_keys
        self.filename = filename
        super().__init__('Experiment config loaded from {} is missing the '
                         'following keys: {}'.format(filename, missing_keys))


class InvalidConfigType(ExperimentRunConfig):

    def __init__(self, key, type, filename):
        self.key = key
        self.type = type
        self.filename = filename
        super().__init__('Experiment config has illegal type for variable '
                         '"{}" in file {}. Expected {}'.format(
                             key, filename, type))


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
        'black_duration': int,
        'c1_duration': typing.Union[int, typing.Tuple[int, int]],
        'c1_color': str,
        'c2_duration': typing.Union[int, typing.Tuple[int, int]],
        'c2_color': str,
        'randomize': bool,
        'sound_device': str,
        'silence_duration': int
    }
    config_keys_set = set(config_keys.keys())

    def __init__(self, filename):
        if isinstance(filename, str):
            with open(filename, 'r') as f:
                config = yaml.load(f, Loader=yaml.Loader)
        elif isinstance(filename, file):
            config = yaml.load(filename, Loader=yaml.Loader)
    
        if not self.config_keys_set.issubset(set(config.keys())):
            raise IncompleteExperimentConfig(
                self.config_keys_set - set(config.keys()), filename)

        for k, t in self.config_keys.items():
            print(k, t, config[k])
            if not check_type(config[k], t):
                raise InvalidConfigType(k, t, filename)

            self.__dict__[k] = config[k]
