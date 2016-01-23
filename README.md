

**NOTICE:** Pandoc 1.16 introduces image attributes.  The new syntax does not allow a space between an image and its attributes.  If you are using pandoc 1.16, then please update your markdown accordingly.


pandoc-fignos 0.7.5.1
=====================

*pandoc-fignos* is a [pandoc] filter for numbering figures and figure references in markdown documents.

Demonstration: Processing [`demo.md`] with `pandoc --filter pandoc-fignos` gives numbered figures and references in [pdf], [tex], [html], [epub], [md] and other formats.

This version of pandoc-fignos was tested using pandoc 1.16.0.1 and 1.15.2, and should be compatible with earlier pandoc versions.  It is known to work under linux, Mac OS X and Windows.

Installation of the filter is straight-forward, with minimal dependencies.  It is simple to use and has been tested extensively.

See also: [pandoc-eqnos], [pandoc-tablenos]

[pandoc]: http://pandoc.org/
[`demo.md`]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo.md
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

Figure numbers and references are required for academic writing, but are not supported natively by pandoc.  Pandoc-fignos is an add-on filter that provides this missing functionality.

The markdown syntax recognized by pandoc-fignos was worked out in [pandoc issue #813].  It seems likely that this will be close to what pandoc ultimately adopts.  Pandoc-fignos is intended to be a transitional package for those who need figure numbers and references now.

[pandoc issue #813]: https://github.com/jgm/pandoc/issues/813


Markdown Syntax
---------------

Consider an image with a caption:

    ![Caption.](image.png)

To associate the label `fig:description` with the image, append the label as an identifier in the image's attributes:

    ![Caption.](image.png){#fig:description}

The prefix `#fig:` is required whereas `description` can be replaced with any combination of letters, numbers, dashes, slashes and underscores.

To reference the figure, use

    @fig:description

or

    {@fig:description}

Curly braces around a reference are stripped from the output.


Usage
-----

To apply the filter, use the following option with pandoc:

    --filter pandoc-fignos

Note that any use of the `--filter pandoc-citeproc` or `--bibliography=FILE` options with pandoc should come *after* the pandoc-fignos filter call.


Details
-------

For tex/pdf output, LaTeX's native `\label` and `\ref` macros are used; for all others the numbers are hard-coded.

Links are constructed for html and pdf output.


Installation
------------

Pandoc-fignos requires [python], a programming language that comes pre-installed on linux and Mac OS X, and which is easily installed [on Windows].  Either python 2.7 or 3.x will do.

Install pandoc-fignos as root using the shell command

    pip install pandoc-fignos 

To upgrade to the most recent release, use

    pip install --upgrade pandoc-fignos 

Pip is a script that downloads and installs modules from the Python Package Index, [PyPI].  It should come installed with your python distribution.


### Installing on Linux ###

If you are running linux, pip may be bundled separately.  On Debian-based systems (including Ubuntu), you can install it as root using

    apt-get update
    apt-get install python-pip

During the install you may be asked to run

    easy_install -U setuptools

owing to the ancient version of setuptools that Debian provides.  The command should be executed as root.  The pip install process should now work.

[python]: https://www.python.org/
[on Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi


Getting Help
------------

If you have any difficulties with pandoc-fignos, please [file an issue] on github.

[file an issue]: https://github.com/tomduck/pandoc-fignos/issues
