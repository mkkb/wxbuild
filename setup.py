from setuptools import setup, find_packages

from visplt import __version__

requires = [
  'wxpython',
  'vispy',
  'numpy',
]

setup(
    name='wxbuild',
    version=__version__,

    url='https://https://github.com/mkkb/wxbuild',
    author='Kristian Borve',
    author_email='mkkb4987@hotmail.com',

    packages=find_packages(),
    
    install_requires=requires,
)
