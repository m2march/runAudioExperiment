import argparse
import sys
import sounddevice
import logging
import logging.config

logger = logging.getLogger('m2.runAudioExperiment.main')

LIST_FLAGS = ['-l', '--list-devices']

def parse_arguments(args):
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
    parser.add_argument(*LIST_FLAGS, 
                        help='List available sound devices',
                        action='store_true'
                       )

    run_args = parser.add_argument_group('Run arguments')
    run_args.add_argument('trial_config', type=argparse.FileType('r'),
                          help='Yaml configuration of the experiment trials.')
    run_args.add_argument('stimuli_list', type=argparse.FileType('r'),
                          help='List of audios to use as stimuli.')
    run_args.add_argument('output_dir', type=str,
                          help='Directory where trial output is saved.')

    run_args.add_argument('-v', choices=[0, 1, 2], default=0, type=int,
                          help='Verbosity level.')
    run_args.add_argument('--debug-durations', action='store_true',
                          help=('This flag enables writing an auxiliary csv '
                                'file describing the actual durations of each '
                                'section of each trial. The file is written '
                                'as '))

    return parser.parse_args()


def main():
    if any([x in sys.argv for x in LIST_FLAGS]):
        print_devices()
    else:
        args = parse_arguments(sys.argv)
        level = {
            0: 'WARN',
            1: 'INFO',
            2: 'DEBUG'
        }[args.v]
        logging.config.dictConfig({
            'version': 1,
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                }
            },
            'loggers': {
                'm2': {
                    'handlers': ['console'],
                    'propagate': '1',
                    'level': level,
                }
            },
            'root': {
            }
        })
        run_experiment(args)


def print_devices():
    print(sounddevice.query_devices())


def run_experiment(args):
    '''
    Executes the trial configuration.

    Args:
        * args.trial_config: open file for the trial config yaml
        * args.stimuli_list: open file for the stimuli list
        * args.output_dir: str indicating directory where output 
            should be saved
    ''' 
    import m2.runAudioExperiment.experiment_config as ec
    import m2.runAudioExperiment.trial_data as td
    import m2.runAudioExperiment.env as environment
    import random
    import psychopy.core
    import psychopy.visual

    logger.info('Loading config from {}.'.format(args.trial_config))
    # Load and verify experiment config
    try:
        exp_config = ec.ExperimentRunConfig(
            args.trial_config, args.stimuli_list, args.output_dir,
            args.debug_durations)
    except ec.ExperimentConfigError as ece:
        print(ece)
        sys.exit()

    logger.info('Preparing environment.')
    # Prepare environment (Psychopy, Sounddevice) 
    env = environment.Environment(exp_config)
    
    logger.info('Creating trials data.')
    # Instance trials data
    trials_data = td.TrialsData(exp_config)

    # Prepare trials
    for trial in trials_data:
        logger.debug('Preparing trial with stimulus {}.'.format(
            trial.stimulus_path
        ))
        trial.prepare(env)

    # Run trials
    for idx, trial in enumerate(trials_data):
        logger.debug('Starting trial #{} with stimulus {}.'.format(
            idx,
            trial.stimulus_path
        ))
        trial.execute(env)

    # Save data
    exp_config.save()
    trials_data.save()
