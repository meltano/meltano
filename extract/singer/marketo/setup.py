from setuptools import setup, find_packages
setup(
    name="meltano-tap-marketo",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'tap-marketo = tap_marketo.cli:main'
        ]
    },
    install_requires=[
        'fire>=0.1.3',
        'pandas>=0.23.4',
        'requests>=2.18.4'
    ],
)

