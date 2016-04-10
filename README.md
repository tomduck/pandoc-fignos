
pandoc-fignos 0.10
==================

*pandoc-fignos* is a [pandoc] filter for numbering figures and figure references in markdown documents.

Demonstration: Processing [demo.md] with `pandoc --filter pandoc-fignos` gives numbered figures and references in [pdf], [tex], [html], [epub], [md] and other formats.

This version of pandoc-eqnos was tested using pandoc 1.17.0.2, 1.16.0.2 and 1.15.2.  It works under linux, Mac OS X and Windows.

Installation of the filter is straight-forward.  It is simple to use and has been tested extensively.

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

Pandoc-fignos may be customized by setting variables in the [metadata block] or on the command line (using `-M KEY=VAL`).  The following variables are supported:

  * `figure-name` - Changes "Figure" at the beginning of a caption
     to a new word (e.g., "Fig." or "图").

[metadata block]: http://pandoc.org/README.html#extension-yaml_metadata_block


Details
-------

For tex/pdf output, LaTeX's `\label` and `\ref` macros are used; for all others the numbers are hard-coded.

Likewise, pandoc-fignos redefines LaTeX's `\figurename` command, and hard codes the figure name for the rest.

Links are constructed for both html and pdf output.


Installation
------------

Pandoc-fignos requires [python], a programming language that comes pre-installed on linux and Mac OS X, and which is easily installed on Windows.  Either python 2.7 or 3.x will do.

[python]: https://www.python.org/
[on Windows]: https://www.python.org/downloads/windows/


### Standard installation ###

Install pandoc-fignos as root using the shell command

    pip install pandoc-fignos 

To upgrade to the most recent release, use

    pip install --upgrade pandoc-fignos 

Pip is a script that downloads and installs modules from the Python Package Index, [PyPI].  It should come installed with your python distribution.

[PyPI]: https://pypi.python.org/pypi


### Installing on linux ###

If you are running linux, pip may be packaged separately from python.  On Debian-based systems (including Ubuntu), you can install pip as root using

    apt-get update
    apt-get install python-pip

During the install you may be asked to run

    easy_install -U setuptools

owing to the ancient version of setuptools that Debian provides.  The command should be executed as root.  You may now follow the [standard installation] procedure given above.

[standard installation]: #standard-installation


### Installing on Windows ###

It is easy to install python on Windows.  First, [download] the latest release.  Run the installer and complete the following steps:

 1. Install Python pane: Check "Add Python 3.5 to path" then
    click "Customize installation".

 2. Optional Features pane: Click "Next".

 3. Advanced Options pane: Optionally check "Install for all
    users" and customize the install location, then click "Install".

Once python is installed, start the "Command Prompt" program.  Depending on where you installed python, you may need to elevate your privileges by right-clicking the "Command Prompt" program and selecting "Run as administrator".  You may now follow the [standard installation] procedure given above.  Be sure to close the Command Prompt program when you have finished.

[download]: https://www.python.org/downloads/windows/


Getting Help
------------

If you have any difficulties with pandoc-fignos, or would like to see a new feature, please [file an issue] on github.

[file an issue]: https://github.com/tomduck/pandoc-fignos/issues
