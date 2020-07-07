from m2.runAudioExperiment import trial_data 

class MockExperimentConfig:

    def __init__(self, black_duration, c1_duration, 
                 c2_duration, silence_duration, out_dir):
        self.black_duration = black_duration
        self.c1_duration = c1_duration
        self.c2_duration = c2_duration
        self.silence_duration = silence_duration
        self.output_dir = out_dir


def test_init():
    config = MockExperimentConfig(100, 200, 300, 400, 'out')

    trial_config = trial_data.SingleTrialData('stim_path', config)

    assert trial_config.black_duration == 100
    assert trial_config.c1_duration == 200
    assert trial_config.c2_duration == 300
    assert trial_config.silence_duration == 400
    assert trial_config.stimulus_path == 'stim_path'
    assert trial_config.recording_path == 'out/stim_path.rec'


def test_init_range():
    config = MockExperimentConfig(100, (200, 300), (300, 400), 400, 'out')

    for _ in range(10):
        trial_config = trial_data.SingleTrialData('stim_path', config)

        assert trial_config.black_duration == 100
        assert trial_config.silence_duration == 400
        assert trial_config.stimulus_path == 'stim_path'
        assert trial_config.recording_path == 'out/stim_path.rec'
        
        assert trial_config.c1_duration >= 200
        assert trial_config.c1_duration <= 300
        assert trial_config.c2_duration >= 300
        assert trial_config.c2_duration <= 400
