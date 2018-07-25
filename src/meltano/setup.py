#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='meltano',
    version='0.1.0-dev',
    description='Meltano framework.',
    author='Meltano Team & Contributors',
    author_email='meltano@gitlab.com',
    url='https://gitlab.com/meltano/meltano',
    packages=find_packages(),
    install_requires=[
        "click",
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
    ],
    entry_points={
        'console_scripts': [
            "meltano = meltano.cli:main"
        ]
    }
)
