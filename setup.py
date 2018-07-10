#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='meltano-common',
      version='0.1.0-alpha0',
      description='Meltano Extract framework.',
      author='Micaël Bergeron',
      author_email='mbergeron@gitlab.com',
      url='https://gitlab.com/meltano/meltano',
      packages=find_packages(),
      install_requires=[
          "psycopg2>=2.7.4",
          "configparser",
          "SQLAlchemy",
          "pandas",
          "pyarrow",
          "pyyaml"
      ]
     )
