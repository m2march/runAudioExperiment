#!/usr/bin/env python

from setuptools import setup

setup(name='runAudioExperiment',
      version='0.1',
      description=('Library and utility to run an tapping audio experiment. '
                   'From "Simple and cheap setup for measuring timed '
                   'responses to auditory stimuli" (Miguel et. al. 2020).'),
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
          'python-gflags',
          'python-magic',
          'numpy',
      ],
      )
