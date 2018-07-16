#!/usr/bin/env python
from setuptools import setup

setup(name='meltano',
      version='0.3.0-dev',
      description='Meltano data science framework.',
      author='Meltano Team & Contributor',
      author_email='meltano@gitlab.com',
      url='https://gitlab.com/meltano/meltano',
      packages=['meltano'],
      install_requires=[
          "meltano-common==0.2.0-dev",
          "fire"
      ],
      entry_points={
          'console_scripts': [
              "meltano = meltano.cli:main"
          ]
       }
     )
