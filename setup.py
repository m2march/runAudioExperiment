#!/usr/bin/env python
import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(name='runAudioExperiment',
      version='0.9.1',
      description=('Library and utility to run an tapping audio experiment. '
                   'From "Simple and cheap setup for measuring timed '
                   'responses to auditory stimuli" (Miguel et. al., under '
                   'review).'),
      long_description=README,
      long_description_content_type='text/markdown',
      url="https://github.com/m2march/runAudioExperiment",
      author='Martin "March" Miguel',
      author_email='m2.march@gmail.com',
      packages=['m2', 'm2.runAudioExperiment'],
      namespace_packages=['m2'],
      entry_points={
          'console_scripts': [
              'runAudioExperiment=m2.runAudioExperiment.cli:main'
          ]
      },
      install_requires=[
          'pydub',
          'numpy',
          'sounddevice',
          'fuzzywuzzy'
      ],
      license='MIT',
)
