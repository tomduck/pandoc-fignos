
pandoc-fignos
=============

*pandoc-fignos* is a [pandoc] filter for numbering figures and figure references.

Demonstration: Using [`demo.md`] as input gives output files in [pdf], [tex], [html], [epub], [md] and other formats.

This version of pandoc-fignos was tested using pandoc 1.14.0.1.

See also: [pandoc-eqnos]

[pandoc]: http://pandoc.org/
[`demo.md`]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo.md
[pdf]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.pdf
[tex]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.tex
[html]: https://rawgit.com/tomduck/pandoc-fignos/master/demos/out/demo.html
[epub]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.epub
[md]: https://github.com/tomduck/pandoc-fignos/blob/master/demos/out/demo.md
[pandoc-eqnos]: https://github.com/tomduck/pandoc-eqnos


Contents
--------

 1. [Rationale](#rationale)
 2. [Markdown Syntax](#markdown-syntax)
 3. [Usage](#usage)
 4. [Details](#details)
 5. [Installation](#installation)


Rationale
---------

Figure numbers and references are required for academic writing, but are not currently supported by pandoc.  It is anticipated that this will eventually change.  Pandoc-fignos is a transitional package for those who need figure numbers and references now.

The syntax for figure numbers and references was worked out in [pandoc issue #813].  It seems likely that this will be close to what pandoc ultimately adopts.

By doing one thing -- and one thing only -- my hope is that pandoc-fignos will permit a relatively painless switch when pandoc provides native support for figure numbers and references.

Installation of the filter is straight-forward, with minimal dependencies.  It is simple to use and has been tested extensively.

[pandoc issue #813]: https://github.com/jgm/pandoc/issues/813


Markdown Syntax
---------------

To tag an image with the label `fig:description`, use

    ![Caption.](image.png) {#fig:description}

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

To keep image attributes in the output (e.g., to be processed by additional filters), use:

    --filter pandoc-fignos -M fignos-keepattrs


Details
-------

For tex/pdf output, LaTeX's native `\label` and `\ref` macros are used; for all others the numbers are hard-coded.

Links are *not* constructed -- just the figure numbers.


Installation
------------

Install pandoc-fignos as root using the bash command

    pip install pandoc-fignos 

To upgrade to the most recent release, use

    pip install --upgrade pandoc-fignos 

If you have any difficulties with it, please [file an issue] on github so that we can help.

[file an issue]: https://github.com/tomduck/pandoc-fignos/issues
