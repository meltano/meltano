#!/usr/bin/env python
from distutils.core import setup

setup(name='meltano-extract-fastly',
      version='0.1.0-dev0',
      description='Meltano extractor for Fastly.',
      author='Meltano Team & Contributor',
      author_email='meltano@gitlab.com',
      url='https://gitlab.com/meltano/meltano',
      packages=['meltano.extract.fastly'],
      install_requires=[
          "aiohttp",
          "SQLAlchemy",
          "psycopg2>=2.7.4",
          "meltano-common"
      ]
     )
