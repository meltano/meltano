#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("VERSION") as version_file:
    version = version_file.read().strip()

requires = [
    'aiohttp==3.4.4',
    'alembic==1.0.11',
    'authlib==0.10',
    'backoff==1.8.0',
    'bcrypt==3.1.6',
    'Cerberus==1.2',
    'click==7.0',
    'click-default-group==1.2.1',
    'colorama==0.3.9',
    'gitpython==2.1.11',
    'gunicorn==19.9.0',
    'jsonschema==2.6.0',
    'markdown==3.0.1',
    'networkx==2.2',
    'pandas==0.24.1',
    'psycopg2==2.7.7',
    'psutil==5.6.3',
    'pyhumps==0.4.0',
    'pypika==0.25.1',
    'python-dotenv==0.10.1',
    'pyyaml==3.13',
    'snowflake-connector-python==1.6.10',
    'snowflake-sqlalchemy==1.1.2',
    'sqlalchemy==1.2.12',
    'fasteners==0.15.0',
    'flask>=1.0.2',
    'flask-cors==3.0.7',
    'flask-executor==0.9.2',
    'flask-sqlalchemy==2.3.2',
    'flask-restful==0.3.7',
    'flask-jwt-extended==3.17.0',
    'flatten-dict==0.1.0',
    'meltano-flask-security==0.1.0',
    'pyhocon==0.3.51',
    'python-dotenv==0.10.1',
    'python-gitlab==1.8.0',
    'simplejson==3.16.0',
    'urllib3==1.23',
    'sqlparse==0.3.0',
    'watchdog==0.9.0',
]

# conflicts resolution, see https://gitlab.com/meltano/meltano/issues/193
conflicts = [
    'aenum==2.1.2',
    'idna==2.7',
]

dev_requires = [
    'asynctest==0.12.2',
    'black==18.9b0',
    'bumpversion==0.5.3',
    'changelog-cli==0.6.2',
    'freezegun==0.3.12',
    'pytest==4.3.1',
    'pytest-asyncio==0.10.0',
    'requests-mock==1.6.0',
    'ipython==7.5.0',
    'pytest-cov==2.6.1',
]

setup(
    name="meltano",
    version=version,
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
