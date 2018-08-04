
#!/usr/bin/env python
from distutils.core import setup

setup(name='bizops-lever',
      version='1.0',
      description='BizOps Lever importer.',
      author='Yannis Roussos',
      author_email='iroussos@gitlab.com',
      url='https://gitlab.com/bizops/bizops',
      packages=['bizops.lever'],
      package_dir={'bizops.lever': 'src'},
     )
