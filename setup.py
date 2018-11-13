#!/usr/bin/env python
try:
  from setuptools import setup, find_namespace_packages
except Exception as e:
  print('You need to upgrade setuptools.')
  print('pip install setuptools --upgrade')
  raise e

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    'aiohttp',
    'backoff',
    'dbt',
    'gitpython',
    'markdown',
    'pandas',
    'psycopg2',
    'pypika',
    'python-dotenv',
    'pyyaml',
    'snowflake-connector-python',
    'snowflake-sqlalchemy',
    'sqlalchemy',
]

api_requires = [
    'flask',
    'flask-cors',
    'flask-sqlalchemy',
]

cli_requires = [
    'click',
]

dev_requires = [
    'pytest',
    'pytest-asyncio',
    'asynctest',
    'black',
    'bumpversion',
]

setup(
    name="meltano",
    version="0.1.2",
    author='Meltano Team & Contributors',
    author_email="meltano@gitlab.com",
    description="Meltano",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/meltano/meltano",
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    package_data={
        'meltano.api': [
            'node_modules',
        ],
        'meltano.core': ['*.yml']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=['pytest-runner'],
    tests_require=dev_requires,
    # run `make requirements.txt` after editing
    install_requires=requires,
    extras_require={
        'api': api_requires,
        'cli': cli_requires,
        'dev': dev_requires,
        'all': [
            *api_requires,
            *cli_requires,
            *dev_requires,
        ],
    },
    entry_points={
        'console_scripts': [
            "meltano = meltano.cli:main [cli]"
        ]
    }
)
