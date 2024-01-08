# setup.py
from setuptools import setup, find_packages
from productsdb import __version__

setup(
    name='productsdb',
    version=__version__,
    packages=find_packages(),
)
