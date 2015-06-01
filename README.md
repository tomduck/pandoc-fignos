
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

This syntax was recommended in the discussion of [pandoc issue #813] by @scaramouche1.

[pandoc issue #813]: https://github.com/jgm/pandoc/issues/813


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

Install pandoc-fignos using:

    $ sudo pip install pandoc-fignos

You will be prompted for your root password.  That's it!

If you have any difficulties with it, please [file an issue] on github so that we can help.

[file an issue]: https://github.com/tomduck/pandoc-fignos/issues
