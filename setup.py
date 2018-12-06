#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    'aiohttp',
    'backoff',
    'click',
    'Cerberus',
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
    'flask',
    'flask-cors',
    'flask-sqlalchemy',
    # conflicts resolution, see https://gitlab.com/meltano/meltano/issues/193
    'idna==2.7',
]

dev_requires = [
    'pytest',
    'pytest-asyncio',
    'asynctest',
    'black',
    'bumpversion',
    'changelog-cli'
]

setup(
    name="meltano",
    version="0.2.1",
    author='Meltano Team & Contributors',
    author_email="meltano@gitlab.com",
    description="Meltano",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/meltano/meltano",
    package_dir={'': 'src'},
    packages=find_packages(where="src"),
    include_package_data=True,
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
        'dev': dev_requires
    },
    entry_points={
        'console_scripts': [
            "meltano = meltano.cli:main"
        ]
    }
)
