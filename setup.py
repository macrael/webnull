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
    version='1.0.1',
    test_suite='tests',
    description='A tool for putting hosts into a blackhole',
    long_description=long_description,
    url='https://github.com/macrael/webnull',
    author='MacRae Linton',
    author_email='macrae@macrael.com',
    license='BSD',
    classifiers=[
        'Environment :: MacOS X',
        'Operating System :: MacOS :: MacOS X',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='distractions productivity',
    py_modules=["webnull"],
    extras_require={
        'test': ['watchdog'],
    },
    entry_points={
        'console_scripts': [
            'webnull=webnull:main',
        ],
    },
)
