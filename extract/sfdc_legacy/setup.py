#!/usr/bin/env python
from distutils.core import setup

setup(name='meltano-extract-salesforce',
      version='1.0',
      description='Meltano Salesforce extractor.',
      author='Micael Bergeron',
      author_email='mbergeron@gitlab.com',
      url='https://gitlab.com/meltano/meltano',
      packages=['meltano.salesforce'],
      package_dir={'meltano.salesforce': 'src'},
      )
