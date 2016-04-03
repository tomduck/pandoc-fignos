"""setup.py - install script for pandoc-fignos."""

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup

LONG_DESCRIPTION = """\
pandoc-fignos is a pandoc filter for numbering figures and figure references.
"""

VERSION = '0.8.1'

setup(
    name='pandoc-fignos',
    version=VERSION,

    author='Thomas J. Duck',
    author_email='tomduck@tomduck.ca',
    description='Figure number filter for pandoc',
    long_description=LONG_DESCRIPTION,
    license='GPL',
    keywords='pandoc figure numbers filter',
    url='https://github.com/tomduck/pandoc-fignos',
    download_url = 'https://github.com/tomduck/pandoc-fignos/tarball/'+VERSION,
    
    install_requires=['pandocfilters', 'pandoc-attributes', 'psutil'],

    py_modules=['pandoc_fignos'],
    entry_points={'console_scripts':['pandoc-fignos = pandoc_fignos:main']},

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python'
        ],
)
