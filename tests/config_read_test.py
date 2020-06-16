import pytest
import typing
import random
import os
import yaml
import m2.runAudioExperiment.experiment_config as cfg

TEST_CONFIG_FN = 'test_config.txt'

@pytest.fixture
def config_fs(fs):
    test_config_path = os.path.join(os.path.dirname(__file__), TEST_CONFIG_FN)
    print(test_config_path)
    fs.add_real_file(test_config_path, target_path=TEST_CONFIG_FN)
    yield fs


def test_config_read(config_fs):
    config = cfg.ExperimentRunConfig(TEST_CONFIG_FN)
    assert config.black_duration == 600
    assert config.c1_duration == 300
    assert config.c1_color == "#afd444"
    assert config.c2_duration == 000
    assert config.c2_color == "#afd444"
    assert config.randomize == False
    assert config.sound_device == "USB Device"
    assert config.silence_duration == 1500


def test_config_read_interval(config_fs):
    with open(TEST_CONFIG_FN, 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)
    
    config['c1_duration'] = (300, 500)

    n_config_fn = '_' + TEST_CONFIG_FN
    config_fs.create_file(n_config_fn, 
                          contents=yaml.dump(config, Dumper=yaml.Dumper))

    config = cfg.ExperimentRunConfig(n_config_fn)
    assert config.black_duration == 600
    assert config.c1_duration == (300, 500)
    assert config.c1_color == "#afd444"
    assert config.c2_duration == 000
    assert config.c2_color == "#afd444"
    assert config.randomize == False
    assert config.sound_device == "USB Device"
    assert config.silence_duration == 1500


@pytest.mark.parametrize('skips_n', range(1, 4))
def test_missing_keys(config_fs, skips_n):
    skips = random.choices(list(cfg.ExperimentRunConfig.config_keys_set), 
                           k=skips_n)
    with open(TEST_CONFIG_FN, 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)
    n_config = {k: v for k, v in config.items() if k not in skips}

    n_config_path = '_' + TEST_CONFIG_FN
    config_fs.create_file(n_config_path, contents=yaml.dump(n_config,
                                                      Dumper=yaml.Dumper))

    try:
        cfg.ExperimentRunConfig(n_config_path)
    except cfg.IncompleteExperimentConfig as e:
        assert e.filename == n_config_path
        assert e.missing_keys == set(skips)
        return

    pytest.fail()


def test_wrong_type(config_fs):
    with open(TEST_CONFIG_FN, 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)

    n_config_fn = '_' + TEST_CONFIG_FN

    # Not int
    n_config = config.copy()
    n_config['black_duration'] = 'not int'
    config_fs.create_file(n_config_fn, 
                          contents=yaml.dump(n_config, Dumper=yaml.Dumper))
    try:
        cfg.ExperimentRunConfig(n_config_fn)
    except cfg.InvalidConfigType as e:
        assert e.key == 'black_duration'
        assert e.type == int
    os.remove(n_config_fn)
    
    # Not str
    n_config = config.copy()
    n_config['c1_color'] = 0
    config_fs.create_file(n_config_fn, 
                          contents=yaml.dump(n_config, Dumper=yaml.Dumper))
    try:
        cfg.ExperimentRunConfig(n_config_fn)
    except cfg.InvalidConfigType as e:
        assert e.key == 'c1_color'
        assert e.type == str
    os.remove(n_config_fn)
    
    # Not dur
    n_config = config.copy()
    n_config['c1_duration'] = 'not dur'
    config_fs.create_file(n_config_fn, 
                          contents=yaml.dump(n_config, Dumper=yaml.Dumper))
    try:
        cfg.ExperimentRunConfig(n_config_fn)
    except cfg.InvalidConfigType as e:
        assert e.key == 'c1_duration'
        assert e.type == typing.Union[int, typing.Tuple[int, int]]
    os.remove(n_config_fn)
