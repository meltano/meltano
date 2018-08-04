
#!/usr/bin/env python
from distutils.core import setup

setup(name='meltano-extract-pings',
      version='1.0',
      description='Meltano Gitlab Pings Extractor.',
      author='Yannis Roussos',
      author_email='iroussos@gitlab.com',
      url='https://gitlab.com/meltano/meltano',
      packages=['meltano.extract.pings'],
      package_dir={'meltano.extract.pings': 'src'},
     )
