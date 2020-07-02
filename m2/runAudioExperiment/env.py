from psychopy import visual
from psychopy import core 
import logging
import sounddevice

LOGGER = logging.getLogger('m2.runAudioExperiment.env')

class Environment:
    '''
    Class collecting enviromental setup to present visual and audio stimuli.
    '''

    def __init__(self, experiment_config):
        self.clock = core.Clock()
        self.window = visual.Window(fullscr=True, color=(-1, -1, -1))
        self.c1_rect = self.create_full_rect(experiment_config.c1_color)
        self.c2_rect = self.create_full_rect(experiment_config.c2_color)
        self.black_rect = self.create_full_rect('black')
        sounddevice.default.device = experiment_config.device_id
        LOGGER.debug('Environment started with sound device: #{} : {}'.format(
            experiment_config.device_id, experiment_config.device_info
        ))

    def create_full_rect(self, color):
        return visual.Rect(self.window, size=(2, 2), pos=(0, 0),
                           lineWidth=0,
                           units="norm", fillColor=color)
