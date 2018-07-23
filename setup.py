#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='meltano',
    version='0.2.0-dev',
    description='Meltano framework.',
    author='Meltano Team & Contributors',
    author_email='meltano@gitlab.com',
    url='https://gitlab.com/meltano/meltano',
    packages=[
        'meltano.schema',
        'meltano.schema.serializers',
        'meltano.stream',
        'meltano.common',
        'meltano.load',
        'meltano.extract'
    ],
    install_requires=[
        "psycopg2>=2.7.4",
        "configparser",
        "SQLAlchemy",
        "pandas",
        "pyarrow",
        "pyyaml",
        "yamlordereddictloader",
        "requests",
        "attrs",
        "aiohttp"
    ]
)
