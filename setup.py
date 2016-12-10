from setuptools import setup, find_packages
from codecs import open
from os import path

from skitza import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='skitza',
    version=__version__,
    description='project description',
    long_description=long_description,
    url='https://github.com/iocube/skitza',
    author='Vladimir Zeifman',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='code generation utility',
    packages=find_packages(),
    package_data={
        'skitza': ['schema.json'],
    },
    install_requires=[
        'click',
        'functools32',
        'Jinja2',
        'jsonschema',
        'MarkupSafe',
        'PyYAML'
    ],
    entry_points={
        'console_scripts': [
            'skitza=skitza.__main__:main'
        ],
    },
)