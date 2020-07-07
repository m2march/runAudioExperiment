import pytest
import os.path
from m2.runAudioExperiment import cli
from m2.runAudioExperiment import trial_data
from adict import adict


def test_trial_data(fs, mocker):
    fs.pause()
    env = mocker.patch('m2.runAudioExperiment.env.Environment')
    mock_config = mocker.MagicMock()
    mock_config.output_dir = 'out_dir'
    mock_config.stimuli_list = list('abc')
    config_class = mocker.patch(
        'm2.runAudioExperiment.experiment_config.ExperimentRunConfig',
        return_value=mock_config
    )
    single_trial_mock = mocker.MagicMock()
    single_trial = mocker.patch(
        'm2.runAudioExperiment.trial_data.SingleTrialData',
        return_value=single_trial_mock
    )
    trials_data = mocker.spy(trial_data, 'TrialsData')

    fs.resume()
    fs.create_dir('out_dir')

    cli.run_experiment(adict({'trial_config': 'trial_config.yaml',
                              'stimuli_list': 'stim_list.txt',
                              'output_dir': 'out_dir',
                              'debug_durations': False}))

    env.assert_called_once()
    config_class.assert_called_once()

    assert single_trial.call_args_list == [((si, mock_config),)
                                           for si in list('abc')]

    assert len(single_trial_mock.prepare.call_args_list) == 3
    assert len(single_trial_mock.execute.call_args_list) == 3
    trials_data.mock_calls[0].return_value.save.assert_called_once()
    mock_config.save.assert_called_once()

    out_file = os.path.join('out_dir', trial_data.TRIAL_SETTINGS_FILENAME)
    with open(out_file) as f:
        print(f.read())
