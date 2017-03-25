# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='webnull',
    version='0.1.0',
    description='A tool for putting hosts into a blackhole',
    long_description=long_description,
    url='https://github.com/macrael/webnull',
    author='MacRae Linton',
    author_email='me@macrael.com',
    license='BSD',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='distractions productivity',
    py_modules=["webnull"],
    extras_require={
        'test': ['watchdog'],
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'webnull=webnull',
        ],
    },
)
