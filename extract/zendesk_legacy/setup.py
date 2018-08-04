
#!/usr/bin/env python
from distutils.core import setup

setup(name='bizops-zendesk',
      version='1.0',
      description='BizOps zendesk importer.',
      author='Micael Bergeron',
      author_email='mbergeron@gitlab.com',
      url='https://gitlab.com/bizops/bizops',
      packages=['bizops.zendesk'],
      package_dir={'bizops.zendesk': 'src'},
     )
