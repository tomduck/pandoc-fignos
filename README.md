

**NOTICE:** Pandoc has introduced changes that require this filter to detect your pandoc version.  If the detection fails, please [file an issue] so that we may fix it.


pandoc-fignos 0.8
=================

*pandoc-fignos* is a [pandoc] filter for numbering figures and figure references in markdown documents.

Demonstration: Processing [demo.md] with `pandoc --filter pandoc-fignos` gives numbered figures and references in [pdf], [tex], [html], [epub], [md] and other formats.

This version of pandoc-fignos was tested using pandoc 1.17.0.2, 1.16.0.2 and 1.15.2, and should be compatible with earlier pandoc versions.  It is known to work under linux, Mac OS X and Windows.

Installation of the filter is straight-forward, with minimal dependencies.  It is simple to use and has been tested extensively.

See also: [pandoc-eqnos], [pandoc-tablenos]

[pandoc]: http://pandoc.org/
[demo.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo.md
[pdf]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.pdf
[tex]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.tex
[html]: https://rawgit.com/tomduck/pandoc-fignos/master/demos/out/demo.html
[epub]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.epub
[md]: https://github.com/tomduck/pandoc-fignos/blob/master/demos/out/demo.md
[pandoc-eqnos]: https://github.com/tomduck/pandoc-eqnos 
[pandoc-tablenos]: https://github.com/tomduck/pandoc-tablenos 


Contents
--------

 1. [Rationale](#rationale)
 2. [Markdown Syntax](#markdown-syntax)
 3. [Usage](#usage)
 4. [Details](#details)
 5. [Installation](#installation)
 6. [Getting Help](#getting-help)


Rationale
---------

Figure numbers and references are required for academic writing, but are not currently supported by pandoc.  Pandoc-fignos is an add-on filter that provides the missing functionality.

The markdown syntax recognized by pandoc-fignos was developed in [pandoc Issue #813] -- see [this post] by [@scaramouche1].  It seems likely that this will be close to what pandoc ultimately adopts.  Pandoc-fignos is a transitional package for those who need figure numbers and references now.

[pandoc Issue #813]: https://github.com/jgm/pandoc/issues/813
[this post]: https://github.com/jgm/pandoc/issues/813#issuecomment-70423503
[@scaramouche1]: https://github.com/scaramouche1


Markdown Syntax
---------------

To number a figure, add the label `fig:id` to its attributes:

    ![Caption.](image.png){#fig:id}

The prefix `#fig:` is required. `id` should be replaced with a unique identifier composed of letters, numbers, dashes, slashes and underscores.

To reference the figure, use

    @fig:id

or

    {@fig:id}

Curly braces around a reference are stripped from the output.

See [demo.md] for an example.

NOTE: pandoc-fignos originally allowed a space between an image and its attributes.  This is no longer allowed owing to the introduction of image attributes in pandoc 1.16.


Usage
-----

To apply the filter, use the following option with pandoc:

    --filter pandoc-fignos

Note that any use of `--filter pandoc-citeproc` or `--bibliography=FILE` should come *after* the pandoc-fignos filter call.


Details
-------

For tex/pdf output, LaTeX's `\label` and `\ref` macros are used; for all others the numbers are hard-coded.

Links are constructed for html and pdf output.


Installation
------------

Pandoc-fignos requires [python], a programming language that comes pre-installed on linux and Mac OS X, and which is easily installed [on Windows].  Either python 2.7 or 3.x will do.


### Standard installation ###

Install pandoc-fignos as root using the shell command

    pip install pandoc-fignos 

To upgrade to the most recent release, use

    pip install --upgrade pandoc-fignos 

Pip is a script that downloads and installs modules from the Python Package Index, [PyPI].  It should come installed with your python distribution.


### Installing on linux ###

If you are running linux, pip may be bundled separately.  On Debian-based systems (including Ubuntu), you can install it as root using

    apt-get update
    apt-get install python-pip

During the install you may be asked to run

    easy_install -U setuptools

owing to the ancient version of setuptools that Debian provides.  The command should be executed as root.  The pip install process should now work.

[python]: https://www.python.org/
[on Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi


### Installing from source ###

You may also choose to install sources [downloaded from github].  After installing the prerequisites ([pandocfilters], [pandoc-attributes] and [psutil]) you may install pandoc-fignos by executing the following command as root in the top directory of your download:

    python setup.py install

[downloaded from github]: https://github.com/tomduck/pandoc-fignos/archive/master.zip
[pandocfilters]: https://github.com/jgm/pandocfilters
[pandoc-attributes]: https://github.com/aaren/pandoc-attributes
[psutil]: https://pypi.python.org/pypi/psutil


Getting Help
------------

If you have any difficulties with pandoc-fignos, please [file an issue] on github.

[file an issue]: https://github.com/tomduck/pandoc-fignos/issues
