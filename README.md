
pandoc-fignos
=============

*pandoc-fignos* is a [pandoc] filter for numbering figures and figure references.

Demonstration: Using [`demo.md`] as input gives output files in [pdf], [tex], [html], [epub], [md] and other formats.

This version of pandoc-fignos was tested using pandoc 1.13.2.

See also: [pandoc-eqnos]


[pandoc]: http://pandoc.org/
[`demo.md`]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo.md
[pdf]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.pdf
[tex]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.tex
[html]: https://rawgit.com/tomduck/pandoc-fignos/master/demos/out/demo.html
[epub]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.epub
[md]: https://github.com/tomduck/pandoc-fignos/blob/master/demos/out/demo.md
[pandoc-eqnos]: https://github.com/tomduck/pandoc-eqnos


Markdown Syntax
---------------

To associate an image with the label `fig:description`, append the label as an id attribute in curly braces:

    ![Caption.](image.png) {#fig:description}

The prefix `#fig:` is required whereas `description` can be replaced with any combination of letters, numbers, dashes, slashes and underscores.

To reference the figure, use

    @fig:description

or

    {@fig:description}

Curly braces around a reference are stripped from the output.

This syntax was recommended in the discussion of [pandoc issue #813].

[pandoc issue #813]: https://github.com/jgm/pandoc/issues/813


Usage
-----

To apply the filter, use the following option with pandoc:

    --filter pandoc-fignos

To keep image attributes in the output (e.g., to be processed by additional filters), use:

    --filter pandoc-fignos -M fignos-keepattrs


Details
-------

For tex/pdf output, LaTeX's native `\label` and `\ref` macros are used; for all others the numbers are hard-coded.

Links are *not* constructed -- just the figure numbers.


Installation
------------

pandoc-fignos is written in [python].  Its dependencies are:

  - setuptools (for setup.py only)
  - pandocfilters
  - pandoc-attributes

If you already have setuptools, then the others will install automatically.

Install pandoc-fignos using:

    $ python setup.py install


[python]: https://python.org/
