#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="meltano",
    version="0.0.1",
    author="Meltano Team",
    author_email="info@gitlab.com",
    description="Meltano",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/meltano/meltano",
    package_dir={'': 'src'},
    packages=[
        'meltano.support',
        'meltano.api',
        'meltano.cli',
        'meltano_plugins.csv_loader',
        'meltano_plugins.postgres_loader',
        'meltano_plugins.fastly',
        'meltano_plugins.sfdc',
        'meltano_plugins.snowflake',
    ],
    package_data={
        'meltano.api': [
            'node_modules',
        ]
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    # run `make requirements.txt` after editing
    install_requires=[
        'aiohttp==3.4.4',
        'backoff==1.6.0',
        'dbt==0.11.1',
        'gitpython==2.1.11',
        'markdown==3.0.1',
        'pandas==0.23.4',
        'psycopg2==2.7.5',
        'python-dotenv==0.9.1',
        'pypika==0.15.7',
        'pyyaml==3.13',
        'sqlalchemy==1.2.12',
        'snowflake-connector-python==1.6.10',
        'snowflake-sqlalchemy==1.1.2'
    ],
    extras_require={
        'api': [
            'flask-cors==3.0.6',
            'flask-sqlalchemy==2.3.2',
            'flask==1.0.2',
        ]
    }
)