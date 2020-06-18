from psychopy import visual
from psychopy import core 


class Environment:
    '''
    Class collecting enviromental setup to present visual and audio stimuli.
    '''

    def __init__(self, expermient_config):
        self.clock = core.Clock()
        self.window = visual.Window(fullscr=True)
