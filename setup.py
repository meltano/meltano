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
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    tests_require=[
        # y'all got no tests
    ],
    # run `make api/requirements.txt` after editing
    install_requires=[
        'aiohttp',
        'backoff',
        'dbt',
        'flask',
        'flask-cors',
        'flask-sqlalchemy',
        'gitpython',
        'markdown',
        'pandas',
        'psycopg2',
        'pypika',
        'pyyaml',
        'sqlalchemy',
    ]
)