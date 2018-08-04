
#!/usr/bin/env python
from distutils.core import setup

setup(name='bizops-netsuite',
      version='1.0',
      description='BizOps NetSuite importer.',
      author='Yannis Roussos',
      author_email='iroussos@gitlab.com',
      url='https://gitlab.com/bizops/bizops',
      packages=['bizops.netsuite'],
      package_dir={'bizops.netsuite': 'src'},
     )
