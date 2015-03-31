'''
Setup configuration
'''

from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path
from pip.req import parse_requirements
from pip.download import PipSession

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(
    'requirements/install.txt', session=PipSession()
)
reqs = [str(ir.req) for ir in install_reqs]

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'CHANGES.rst'), encoding='utf-8') as f:
    long_description = '%s\n\n%s' % (long_description, f.read())

setup(
    name='bulby',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1.dev0',
    description='Manages the phillips hue lightbulbs',
    long_description=long_description,
    url='https://github.com/sontek/bulby.git',
    author='John Anderson',
    author_email='sontek@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='etl extract transform load',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=reqs,
    setup_requires=['setuptools-git'],
    entry_points={
        'paste.app_factory': [
            'main=liberator:main',
        ],
    },
)
