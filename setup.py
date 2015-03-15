
from setuptools import setup, find_packages


long_description = """\
pandoc-fignos is a pandoc filter for numbering figures and figure references.
"""

setup(
    name = 'pandoc-fignos',
    version = '0.1',

    author = 'Thomas J. Duck',
    author_email = 'tomduck@tomduck.ca',
    description = 'Figure number filter for pandoc',
    long_description=long_description,
    license = 'GPL',
    keywords = 'pandoc figure numbers filter',
    url='https://github.com/tomduck/pandoc-fignos',

    install_requires=['pandocfilters', 'pandoc-attributes'],

    py_modules = ['pandoc_fignos'],
    entry_points = { 'console_scripts':
                     ['pandoc-fignos = pandoc_fignos:main'] },

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python' ]
)
