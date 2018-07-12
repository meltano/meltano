#!/usr/bin/env python
from distutils.core import setup

setup(name='meltano',
      version='0.1.0-dev0',
      description='Meltano data science framework.',
      author='Meltano Team & Contributor',
      author_email='meltano@gitlab.com',
      url='https://gitlab.com/meltano/meltano',
      packages=['meltano.submodule'],
      install_requires=[
          "meltano-common==0.2.0-dev",
          "fire"
      ]
     )
