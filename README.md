
pandoc-fignos 0.18.2
====================

*pandoc-fignos* is a [pandoc] filter that numbers figures and figure references in processed markdown documents.  A cross-referencing syntax is added to markdown for this purpose.

Demonstration: Processing [demo.md] with `pandoc --filter pandoc-fignos` gives numbered figures and references in [pdf], [tex], [html], [epub], [md] and other formats.

This version of pandoc-fignos was tested using pandoc 1.15 - 1.18.  It works under linux, Mac OS X and Windows.  Older versions and other platforms can be supported on request.  I am pleased to receive bug reports and feature requests on the project's [Issues tracker].

If you find pandoc-fignos useful, then please encourage further development by giving it a star [on GitHub].

See also: [pandoc-eqnos], [pandoc-tablenos]

[pandoc]: http://pandoc.org/
[demo.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo.md
[pdf]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.pdf
[tex]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.tex
[html]: https://rawgit.com/tomduck/pandoc-fignos/master/demos/out/demo.html
[epub]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.epub
[md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.md
[manual]: https://github.com/fermiumlabs/Hall-effect-apparatus/releases/latest/
[Issues tracker]: https://github.com/tomduck/pandoc-fignos/issues
[on GitHub]:  https://github.com/tomduck/pandoc-fignos
[pandoc-eqnos]: https://github.com/tomduck/pandoc-eqnos
[pandoc-tablenos]: https://github.com/tomduck/pandoc-tablenos


Contents
--------

 1. [Usage](#usage)
 2. [Markdown Syntax](#markdown-syntax)
 3. [Customization](#customization)
 4. [Technical Details](#technical-details)
 5. [Installation](#installation)
 6. [Getting Help](#getting-help)


Usage
-----

To apply the filter during document processing, use the following option with pandoc:

    --filter pandoc-fignos

Note that any use of `--filter pandoc-citeproc` or `--bibliography=FILE` should come *after* the pandoc-fignos filter call.


Markdown Syntax
---------------

The markdown syntax extension used by pandoc-fignos was developed in [pandoc Issue #813] -- see [this post] by [@scaramouche1].

To mark a figure for numbering, add the label `fig:id` to its attributes:

    ![Caption.](image.png){#fig:id}

Alternatively, use [reference link] attributes.  The prefix `#fig:` is required. `id` should be replaced with a unique identifier composed of letters, numbers, dashes, slashes and underscores.  If `id` is omitted then the figure will be numbered but unreferenceable.

To reference the figure, use

    @fig:id

or

    {@fig:id}

Curly braces around a reference are stripped from the output.

Demonstration: Processing [demo.md] with `pandoc --filter pandoc-fignos` gives numbered figures and references in [pdf], [tex], [html], [epub], [md] and other formats.

[pandoc Issue #813]: https://github.com/jgm/pandoc/issues/813
[this post]: https://github.com/jgm/pandoc/issues/813#issuecomment-70423503
[@scaramouche1]: https://github.com/scaramouche1
[reference link]: http://pandoc.org/MANUAL.html#reference-links


#### Clever References ####

Writing markdown like

    See fig. @fig:id.

seems a bit redundant.  Pandoc-fignos supports "clever referencing" via single-character modifiers in front of a reference.  You can write

     See +@fig:id.

to have the reference name (i.e., "fig.") automatically generated.  The above form is used mid-sentence.  At the beginning of a sentence, use

     *@fig:id

instead.  If clever referencing is enabled by default (see [Customization](#customization), below), you can disable it for a given reference using![The disabling modifier "!" is used instead of "-" because [pandoc unnecessarily drops minus signs] in front of references.]

    !@fig:id

Demonstration: Processing [demo2.md] with `pandoc --filter pandoc-fignos` gives numbered figures and references in [pdf][pdf2], [tex][tex2], [html][html2], [epub][epub2], [md][md2] and other formats.

Note: If you use `*fig:id` and emphasis (e.g., `*italics*`) in the same sentence, then you must backslash escape the `*` in the clever reference; e.g., `\*fig:id`.

[demo2.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo2.md
[pdf2]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo2.pdf
[tex2]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo2.tex
[html2]: https://rawgit.com/tomduck/pandoc-fignos/master/demos/out/demo2.html
[epub2]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo2.epub
[md2]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo2.md
[pandoc unnecessarily drops minus signs]: https://github.com/jgm/pandoc/issues/2901


#### Tagged Figures ####

You may optionally override the figure number by placing a tag in a figure's attributes block as follows:

    ![Caption.](image.png){#fig:id tag="B.1"}

The tag may be arbitrary text, or an inline equation such as `$\text{B.1}'$`.  Mixtures of the two are not currently supported.


Customization
-------------

Pandoc-fignos may be customized by setting variables in the [metadata block] or on the command line (using `-M KEY=VAL`).  The following variables are supported:

  * `fignos-caption-name` - Sets the name at the beginning of a
    caption (e.g., change it from "Figure to "Fig." or "图");

  * `fignos-cleveref` or just `cleveref` - Set to `On` to assume "+"
    clever references by default;

  * `fignos-plus-name` - Sets the name of a "+" reference 
    (e.g., change it from "fig." to "figure"); and

  * `fignos-star-name` - Sets the name of a "*" reference 
    (e.g., change it from "Figure" to "Fig.").

  * `xnos-cleveref-fake` - Sets cleveref faking On/Off (LaTeX/pdf
    only).  See [Technical Details](#technical-details), below.

[metadata block]: http://pandoc.org/README.html#extension-yaml_metadata_block

Demonstration: Processing [demo3.md] with `pandoc --filter pandoc-fignos` gives numbered figures and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [md][md3] and other formats.

[demo3.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo3.md
[pdf3]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo3.pdf
[tex3]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo3.tex
[html3]: https://rawgit.com/tomduck/pandoc-fignos/master/demos/out/demo3.html
[epub3]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo3.epub
[md3]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo3.md


#### Pandoc Flags ####

Some of pandoc's command-line flags impact figure numbering:

  * `-N`, `--number-sections`: Numbers section (or chapter) headings
    in LaTeX/pdf, ConTeXt, html, and epub output.  Figure numbers
    are given in X.Y format, where X is the section (or chapter)
    number and Y is the figure number.  Figure numbers restart at 1
    for each section (or chapter).  See also pandoc's 
    `--top-level-division` flag and `documentclass` meta variable.


#### Latex/PDF Specializations ####

To make the figure caption label bold, add `\usepackage[labelfont=bf]{caption}` to the LaTeX header.  See pandoc's `--include-in-header` flag, and also the [LaTeX caption package] documentation.

[LaTeX caption package]: https://www.ctan.org/pkg/caption


Technical Details
-----------------

For TeX/pdf output:

  * The `\label` and `\ref` macros are used for figure labels and
    references;
  * `\figurename` is set for the caption name;
  * Tags are supported by temporarily redefining `\thefigure` 
    around a figure; and
  * The clever referencing macros `\cref` and `\Cref` are used
    if they are available (i.e. included in your LaTeX template via
    `\usepackage{cleveref}`), otherwise they are faked.  Set the 
    meta variable `xnos-cleveref-fake` to `Off` to disable cleveref
    faking.

For all other formats the numbers, caption name, and clever references are hard-coded into the output.

Links are constructed for both html and pdf output.


Installation
------------

Pandoc-fignos requires [python], a programming language that comes pre-installed on linux and Mac OS X, and which is easily installed on Windows.  Either python 2.7 or 3.x will do.

[python]: https://www.python.org/


#### Standard installation ####

Install pandoc-fignos as root using the shell command

    pip install pandoc-fignos 

To upgrade to the most recent release, use

    pip install --upgrade pandoc-fignos 

Pip is a program that downloads and installs modules from the Python Package Index, [PyPI].  It should come installed with your python distribution.

[PyPI]: https://pypi.python.org/pypi


#### Installing on linux ####

If you are running linux, pip may be packaged separately from python.  On Debian-based systems (including Ubuntu), you can install pip as root using

    apt-get update
    apt-get install python-pip

During the install you may be asked to run

    easy_install -U setuptools

owing to the ancient version of setuptools that Debian provides.  The command should be executed as root.  You may now follow the [standard installation] procedure given above.

[standard installation]: #standard-installation


#### Installing on Windows ####

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

If you have any difficulties with pandoc-fignos, or would like to see a new feature, please [file an Issue] on GitHub.

[file an Issue]: https://github.com/tomduck/pandoc-fignos/issues
