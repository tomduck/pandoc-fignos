
pandoc-fignos
=============

*pandoc-fignos* is a [pandoc] filter for numbering figures and figure references.

Demonstration files are given in the `demos` directory.  Using [`demos/demo.md`] as input gives output files in [pdf], 
[tex]` `(fragment), [html], [epub], [md] and other formats.

This version of pandoc-fignos was tested using pandoc 1.13.2.

[pandoc]: http://pandoc.org/
[`demos/demo.md`]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo.md
[pdf]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.pdf
[tex]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.tex
[html]: https://rawgit.com/tomduck/pandoc-fignos/master/demos/out/demo.html
[epub]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/out/demo.epub
[md]: https://github.com/tomduck/pandoc-fignos/blob/master/demos/out/demo.md


Markdown Syntax
---------------

To label an image with `fig:desc`, append attributes in curly braces:

    ![Caption.](image.png) {#fig:desc}

The tag `#fig:` is required whereas `desc` can be replaced with any combination of letters, numbers, dashes, slashes and underscores.

To reference the figure, use

    @fig:desc

or

    {@fig:desc}

Curly braces around a reference are stripped from the output.

The syntax was taken from the consensus emerging from the discussion of [pandoc issue #813].

[pandoc issue #813]: https://github.com/jgm/pandoc/issues/813


Usage
-----

To apply the filter, use the following option with pandoc:

    --filter pandoc-fignos

To keep image attributes in the output (e.g., to be processed by additional filters), use:

    --filter pandoc-fignos -M fignos-keepattrs


Installation
------------

Installation requires the following python packages:

  - setuptools
  - pandocfilters
  - pandoc-attributes

If you don't have setuptools, it can be installed by executing

    $ pip install setuptools

as root.  The other packages will be automatically installed in the setup process.

To install the pandoc-fignos library and filter script from source, execute the following (as root):

    $ python setup.py install


Details
-------

For tex/pdf output, LaTeX's native `\label` and `\ref` macros are used; for all others the numbers are hard-coded.

Links are *not* constructed -- just the figure numbers.  A filter option may be used to keep image attributes in place so that further processing (e.g., by other filters) can be performed.
