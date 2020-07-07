import pytest
import typing
import random
import os
import yaml
import sounddevice
import m2.runAudioExperiment.experiment_config as cfg

TEST_CONFIG_FN = 'test_config.txt'
STIM_LIST_FN = 'stim_list.txt'
OUTDIR_FN = 'outdir'
STIM_LIST = list('abc')

@pytest.fixture
def config_fs(fs):
    test_config_path = os.path.join(os.path.dirname(__file__), TEST_CONFIG_FN)
    print(test_config_path)
    fs.add_real_file(test_config_path, target_path=TEST_CONFIG_FN)

    for x in STIM_LIST:
        fs.create_file(x)

    fs.create_file(STIM_LIST_FN, contents='\n'.join(STIM_LIST))
    yield fs


@pytest.fixture
def sound_mocker(mocker):
    sound_device_mock = [{'name': 'USB Device'}]
    mocker.patch('sounddevice.query_devices',
                 return_value=sound_device_mock)
    yield mocker


def test_config_read(config_fs, sound_mocker):
    config = cfg.ExperimentRunConfig(TEST_CONFIG_FN, STIM_LIST_FN, OUTDIR_FN)
    assert config.black_duration == 600
    assert config.c1_duration == 300
    assert config.c1_color == "#afd444"
    assert config.c2_duration == 000
    assert config.c2_color == "#afd444"
    assert config.randomize == False
    assert config.sound_device == "USB Device"
    assert config.silence_duration == 1500
    assert config.output_dir == OUTDIR_FN
    assert config.stimuli_list == list('abc')


def test_config_read_interval(config_fs, sound_mocker):
    with open(TEST_CONFIG_FN, 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)
    
    config['c1_duration'] = (300, 500)

    n_config_fn = '_' + TEST_CONFIG_FN
    config_fs.create_file(n_config_fn, 
                          contents=yaml.dump(config, Dumper=yaml.Dumper))

    config = cfg.ExperimentRunConfig(n_config_fn, STIM_LIST_FN, OUTDIR_FN)
    assert config.black_duration == 600
    assert config.c1_duration == (300, 500)
    assert config.c1_color == "#afd444"
    assert config.c2_duration == 000
    assert config.c2_color == "#afd444"
    assert config.randomize == False
    assert config.sound_device == "USB Device"
    assert config.silence_duration == 1500


@pytest.mark.parametrize('skips_n', range(1, 4))
def test_missing_keys(config_fs, skips_n, sound_mocker):
    skips = random.choices(list(cfg.ExperimentRunConfig.config_keys_set), 
                           k=skips_n)
    with open(TEST_CONFIG_FN, 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)
    n_config = {k: v for k, v in config.items() if k not in skips}

    n_config_path = '_' + TEST_CONFIG_FN
    config_fs.create_file(n_config_path, contents=yaml.dump(n_config,
                                                      Dumper=yaml.Dumper))

    try:
        cfg.ExperimentRunConfig(n_config_path, STIM_LIST_FN, OUTDIR_FN)
        pytest.fail()
    except cfg.IncompleteExperimentConfig as e:
        assert e.filename == n_config_path
        assert e.missing_keys == set(skips)
        return

    pytest.fail()


def test_wrong_type(config_fs, sound_mocker):
    with open(TEST_CONFIG_FN, 'r') as f:
        config = yaml.load(f, Loader=yaml.Loader)

    n_config_fn = '_' + TEST_CONFIG_FN

    # Not int
    n_config = config.copy()
    n_config['black_duration'] = 'not int'
    config_fs.create_file(n_config_fn, 
                          contents=yaml.dump(n_config, Dumper=yaml.Dumper))
    try:
        cfg.ExperimentRunConfig(n_config_fn, STIM_LIST_FN, OUTDIR_FN)
        pytest.fail()
    except cfg.InvalidConfigType as e:
        assert e.key == 'black_duration'
        assert e.type == typing.Union[typing.Tuple[int, int], int]
    os.remove(n_config_fn)
    
    # Not str
    n_config = config.copy()
    n_config['c1_color'] = 0
    config_fs.create_file(n_config_fn, 
                          contents=yaml.dump(n_config, Dumper=yaml.Dumper))
    try:
        cfg.ExperimentRunConfig(n_config_fn, STIM_LIST_FN, OUTDIR_FN)
        pytest.fail()
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
        cfg.ExperimentRunConfig(n_config_fn, STIM_LIST_FN, OUTDIR_FN)
        pytest.fail()
    except cfg.InvalidConfigType as e:
        assert e.key == 'c1_duration'
        assert e.type == typing.Union[int, typing.Tuple[int, int]]
    os.remove(n_config_fn)


# TODO: Test existing stim error
def test_non_existing_stim_error(config_fs, sound_mocker):
    config_fs.create_file('stim2.txt', contents='\n'.join(list('abdc')))

    try:
        config = cfg.ExperimentRunConfig(TEST_CONFIG_FN, 'stim2.txt', 
                                         OUTDIR_FN)
        pytest.fail()
    except cfg.MissingStimuliFiles as msf:
        pass


# TODO: Test empty output dir error
def test_existing_output_dir(config_fs, sound_mocker):
    config_fs.create_dir(OUTDIR_FN)

    cfg.ExperimentRunConfig(TEST_CONFIG_FN, STIM_LIST_FN, OUTDIR_FN)

    # No errors expected

def test_nonempty_existing_output_dir(config_fs, sound_mocker):
    config_fs.create_dir(OUTDIR_FN)
    config_fs.create_file(os.path.join(OUTDIR_FN, 'out'))

    try:
        cfg.ExperimentRunConfig(TEST_CONFIG_FN, STIM_LIST_FN, OUTDIR_FN)
        pytest.fail()
    except cfg.IllegalOutputDirectory as iod:
        pass


# TODO: Test non existing sound device error
def test_missing_sound_device(config_fs, mocker):
    mocker.patch('sounddevice.query_devices', 
                 return_value=[{'name': 'Intel'}, {'name': 'Default'}])

    try:
        cfg.ExperimentRunConfig(TEST_CONFIG_FN, STIM_LIST_FN, OUTDIR_FN)
        pytest.fail()
    except cfg.NoMatchingDeviceFound as nmdf:
        pass
