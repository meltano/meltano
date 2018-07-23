#!/usr/bin/env python
from distutils.core import setup

setup(name='meltano-load-postgresql',
      version='0.1.0-dev0',
      description='Meltano loader for PostgreSQL.',
      author='Meltano Team & Contributor',
      author_email='meltano@gitlab.com',
      url='https://gitlab.com/meltano/meltano',
      packages=['meltano.load.postgresql'],
      install_requires=[
          "SQLAlchemy",
          "psycopg2>=2.7.4",
          "meltano-common"
      ]
     )
