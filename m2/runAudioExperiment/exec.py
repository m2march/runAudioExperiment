import argparse
import m2.runAudioExperiment.experiment_config as ec
import m2.runAudioExperiment.trial_dat as td
import m2.runAudioExperiment.env as environment
import random
import psychopy.core
import psychopy.visual

def parse_arguments():
    '''
    Creates the argument parser and returns parsed arguments.
    '''
    parser = argparse.ArgumentParser(
        description=(
            'Executes an audio experiment with trials defined by config.\n\n'
            'The script is the implementation of the tool to execute trials '
            'as described in "Simple and cheap setup for measuring timed '
            'responses to auditory stimuli" (Miguel et. al. 2020).'
        )
    )
    parser.add_argument('trial_config', type=argparse.FileType('r'),
                        help='Yaml configuration of the experiment trials.')
    parser.add_argument('stimuli_list', type=argparse.FileType('r'),
                        help='List of audios to use as stimuli.')
    parser.add_argument('output_dir', type=str,
                        help='Directory where trial output is saved.')

    return parser.parse_arguments()


def main(args):
    '''
    Executes the trial configuration.

    Args:
        * args.trial_config: open file for the trial config yaml
        * args.stimuli_list: open file for the stimuli list
        * args.output_dir: str indicating directory where output 
            should be saved
    ''' 
    # Load and verify experiment config
    try:
        exp_config = ec.ExperimentRunConfig(
            args.trial_config, args.stimuli_list, args.output_dir)
    except ExperimentConfigError as ece:
        print(ece)

    # Instance trials data
    trials_data = td.TrialsData(exp_config)

    # Prepare environment (Psychopy, Sounddevice) 
    env = environment.Environment(exp_config)

    # Prepare trials
    for trial in trials_data:
        trial.prepare(env)

    # Run trials
    for trial in trials_data:
        trial.execute(env)
