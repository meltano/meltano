#!/usr/bin/env python
from distutils.core import setup

setup(name='meltano-load-postgresql',
      version='0.1.0-dev0',
      description='Meltano loader for PostgreSQL.',
      author='Micaël Bergeron',
      author_email='mbergeron@gitlab.com',
      url='https://gitlab.com/meltano/meltano',
      packages=['meltano', 'elt'],
      install_requires=[
          "SQLAlchemy",
          "psycopg2>=2.7.4",
          "meltano-common==0.1.0a1"
      ]
     )
