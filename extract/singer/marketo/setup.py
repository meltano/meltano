from setuptools import setup, find_packages
setup(
    name="meltano-tap-marketo",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tap-marketo = tap_marketo.cli:cli'
        ]
    },
    install_requires=[
        'click>=6',
        'pandas>=0.23',
        'requests>=2.18'
    ],
)

