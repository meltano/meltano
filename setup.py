#!/usr/bin/env python
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="meltano",
    version="0.0.1",
    author='Meltano Team & Contributors',
    author_email="meltano@gitlab.com",
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
        'click',
        'aiohttp',
        'backoff',
        'dbt',
        'gitpython',
        'markdown',
        'pandas',
        'psycopg2',
        'pypika',
        'pyyaml',
        'sqlalchemy',
        'snowflake-connector-python',
        'snowflake-sqlalchemy'
    ],
    extras_require={
        'api': [
            'flask-cors',
            'flask-sqlalchemy',
            'flask',
        ]
    },
    entry_points={
        'console_scripts': [
            "meltano = meltano.cli:main"
        ]
    }
)
