"""
Installation:
    pip install git+https://github.com/alpha-xone/xone.git

Pypi:
    # Presetup
    pip install pandas
"""

from setuptools import setup, find_packages
from os import path

from io import open

CUR_PATH = path.abspath(path.dirname(__file__))

with open(path.join(CUR_PATH, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


if __name__ == '__main__':

    setup(
        name='xone',
        version='0.1.0',
        description='Time series analysis utilities',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/alpha-xone/xone',
        author='Alpha',
        keywords='time series analysis utilities',
        packages=find_packages(exclude=['contrib', 'docs', 'tests']),
        install_requires=['pandas'],
        # extras_require=dict(dev=[], test=[],),
        # package_data=dict(sample=[]),
        # data_files=[('my_data', ['data/data_file'])],
        # entry_points=dict(),
        classifiers=(
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
        ),
    )
