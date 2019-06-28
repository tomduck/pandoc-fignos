

**Notice:** This beta release may be installed using

    pip install pandoc-fignos --upgrade --pre --user

**New in 2.0.0:** This is a major release which is easier to use at the cost of minor incompatibilities with previous versions.

[more...](#whats-new).


pandoc-fignos 2.0.0
===================

*pandoc-fignos* is a [pandoc] filter for numbering figures and their references when converting markdown documents to other formats.

Demonstration: Processing [demo3.md] with pandoc + pandoc-fignos gives numbered figures and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats.

This version of pandoc-fignos was tested using pandoc 1.15.2 - 2.7.3,<sup>[1](#footnote1)</sup> and may be used with linux, macOS, and Windows. Bug reports and feature requests may be posted on the project's [Issues tracker].  If you find pandoc-fignos useful, then please kindly give it a star [on GitHub].

Pandoc-fignos is easy to install and use, and equally supports pdf/latex, html, and epub output formats.  Its output may be customized, and helpful messages are provided when errors are detected.

See also: [pandoc-eqnos], [pandoc-tablenos]

[pandoc]: http://pandoc.org/
[Issues tracker]: https://github.com/tomduck/pandoc-fignos/issues
[on GitHub]:  https://github.com/tomduck/pandoc-fignos
[pandoc-eqnos]: https://github.com/tomduck/pandoc-eqnos
[pandoc-tablenos]: https://github.com/tomduck/pandoc-tablenos


Contents
--------

 1. [Installation](#installation)
 2. [Usage](#usage)
 3. [Markdown Syntax](#markdown-syntax)
 4. [Customization](#customization)
 5. [Technical Details](#technical-details)
 6. [Getting Help](#getting-help)
 7. [Development](#development)
 8. [What's New](#whats-new)


Installation
------------

Pandoc-fignos requires [python], a programming language that comes pre-installed on macOS and linux.  It is easily installed on Windows -- see [here](https://realpython.com/installing-python/).  Either python 2.7 or 3.x will do.

Pandoc-fignos may be installed and upgraded using the shell command

    pip install pandoc-fignos --user --upgrade

Pip is a program that downloads and installs software from the Python Package Index, [PyPI].  It normally comes installed with a python distribution.

Instructions for installing from source are given in [README.developers].

[python]: https://www.python.org/
[PyPI]: https://pypi.python.org/pypi
[README.developers]: README.developers


Usage
-----

Pandoc-fignos is activated by using the

    --filter pandoc-fignos

option with pandoc.  Any use of `--filter pandoc-citeproc` or `--bibliography=FILE` should come *after* the pandoc-fignos filter option.


Markdown Syntax
---------------

The cross-referencing syntax used by pandoc-fignos was developed in [pandoc Issue #813] -- see [this post] by [@scaramouche1].

To mark a figure for numbering, add an identifier to its attributes:

    ![Caption.](image.png){#fig:id}

The prefix `#fig:` is required. `id` should be replaced with a unique string composed of letters, numbers, dashes and underscores.  If `id` is omitted then the figure will be numbered but unreferenceable.  Alternatively, [reference link] attributes may be used.

To reference the figure, use

    @fig:id

or

    {@fig:id}

Curly braces around a reference are stripped from the output.

Demonstration: Processing [demo.md] with pandoc + pandoc-fignos gives numbered figures and references in [pdf], [tex], [html], [epub], [docx] and other formats.

[pandoc Issue #813]: https://github.com/jgm/pandoc/issues/813
[this post]: https://github.com/jgm/pandoc/issues/813#issuecomment-70423503
[@scaramouche1]: https://github.com/scaramouche1
[reference link]: http://pandoc.org/MANUAL.html#reference-links
[demo.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo.md
[pdf]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo.pdf
[tex]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo.tex
[html]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo.html
[epub]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo.epub
[docx]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo.docx


### Clever References ###

Writing markdown like

    See fig. @fig:id.

seems a bit redundant.  Pandoc-fignos supports "clever references" via single-character modifiers in front of a reference.  Users may write

     See +@fig:id.

to have the reference name (i.e., "fig.") automatically generated.  The above form is used mid-sentence; at the beginning of a sentence, use

     *@fig:id

instead.  If clever references are enabled by default (see [Customization](#customization), below), then users may disable it for a given reference using<sup>[2](#footnote2)</sup>

    !@fig:id

Demonstration: Processing [demo2.md] with pandoc + pandoc-fignos gives numbered figures and references in [pdf][pdf2], [tex][tex2], [html][html2], [epub][epub2], [docx][docx2] and other formats.

Note: When using `*fig:id` and emphasis (e.g., `*italics*`) in the same sentence, the `*` in the clever reference must be backslash-escaped; i.e., `\*fig:id`.

[demo2.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo2.md
[pdf2]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo2.pdf
[tex2]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo2.tex
[html2]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo2.html
[epub2]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo2.epub
[docx2]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo2.docx


### Tagged Figures ###

The figure number may be overridden by placing a tag in the figure's attributes block:

    ![Caption.](image.png){#fig:id tag="B.1"}

The tag may be arbitrary text, or an inline equation such as `$\text{B.1}'$`.  Mixtures of the two are not currently supported.


Customization
-------------

Pandoc-fignos may be customized by setting variables in the [metadata block] or on the command line (using `-M KEY=VAL`).  The following variables are supported:

  * `fignos-warning-level` or `xnos-warning-level` - Set to `0` for
    no warnings, `1` for critical warnings (default), or `2` for
    critical warnings and informational messages.  Warning level 2
    should be used when troubleshooting.

  * `fignos-cleveref` or `xnos-cleveref` - Set to `True` to assume "+"
    clever references by default;

  * `xnos-capitalise` - Capitalizes the names of "+" clever
    references (e.g., change from "fig." to "Fig.");

  * `fignos-plus-name` - Sets the name of a "+" clever reference
    (e.g., change it from "fig." to "figure"); and

  * `fignos-star-name` - Sets the name of a "*" clever reference
    (e.g., change it from "Figure" to "Fig.").

  * `fignos-caption-name` - Sets the name at the beginning of a
    caption (e.g., change it from "Figure to "Fig." or "图");

  * `fignos-caption-separator` or `xnos-caption-separator` - Sets 
    the caption separator (e.g., the colon in "Figure 1:") to
    something else.  It must be one of none, colon,
    period, space, quad, and newline; and

  * `fignos-number-sections` or `xnos-number-sections` - Set to
    `True` to number figures by section (e.g., Fig. 1.1, 1.2, etc in
     Section 1, and Fig 2.1, 2.2, etc in Section 2).  This feature
     should be used together with pandoc's `--number-sections`
     [option](https://pandoc.org/MANUAL.html#option--number-sections)
     enabled for LaTeX/pdf, html, and epub output.  For docx,
     use [docx custom styles] instead.

Note that variables beginning with `fignos-` apply to only pandoc-fignos, whereas variables beginning with `xnos-` apply to all three of pandoc-fignos/eqnos/tablenos.

Demonstration: Processing [demo3.md] with pandoc + pandoc-fignos gives numbered figures and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats.

[metadata block]: http://pandoc.org/README.html#extension-yaml_metadata_block
[docx custom styles]: https://pandoc.org/MANUAL.html#custom-styles
[demo3.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo3.md
[pdf3]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo3.pdf
[tex3]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo3.tex
[html3]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo3.html
[epub3]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo3.epub
[docx3]: https://raw.githack.com/tomduck/pandoc-fignos/master/demos/out/demo3.docx


Technical Details
-----------------

### TeX/pdf Output ###

During processing, pandoc-fignos inserts packages and supporting TeX into the `header-includes` metadata field.  To see what is inserted, set the `fignos-warninglevel` meta variable to `2`.  Note that any use of pandoc's `--include-in-header` option [overrides](https://github.com/jgm/pandoc/issues/3139) all `header-includes`.

An example reference in TeX looks like

~~~latex
See \cref{fig:1}.
~~~

An example figure looks like

~~~latex
\begin{figure}
  \hypertarget{fig:1}{%
    \centering
    \includegraphics[width=1in,height=\textheight]{img/fig-1.png}
    \caption{The number one.}\label{fig:1}
  }
\end{figure}
~~~

Other details:

  * The `cleveref` and `caption` packages are used for clever
    references and caption control, respectively; 
  * The `\label` and `\ref` macros are used for figure labels and
    references, respectively (`\Cref` and `\cref` are used for
    clever reference)s;
  * Clever reference names are set with `\Crefname` and `\crefname`;
  * The caption name is set with`\figurename`;
  * Tags are supported by way of a custom environment that
    temporarily redefines `\thefigure`; and
  * Caption prefixes (e.g., "Figure 1:") are disabled for
    unnumbered figures by way of a custom environment that uses
    `\captionsetup`.


### Html/Epub Output ###

An example reference in html looks like

~~~html
See fig. <a href="#fig:1">1</a>.
~~~

An example figure looks like

~~~html
<div id="fig:1" class="fignos">
  <figure>
    <img src="img/fig-1.png" style="width:1in" alt="" />
    <figcaption>
      <span>Figure 1:</span> The number one.
    </figcaption>
  </figure>
</div>
~~~

The figure and its number are wrapped in a `<div></div>` with an `id` for linking and with class `fignos` to allow for css styling.


### Docx Output ###

Docx OOXML output is under development and subject to change.  Native capabilities will be used wherever possible.


Getting Help
------------

If you have any difficulties with pandoc-fignos, or would like to see a new feature, then please submit a report to our [Issues tracker].


Development
-----------

Full docx support is awaiting input from a knowledgeable expert on how to structure the OOXML.

Pandoc-fignos will continue to support pandoc 1.15-onward and python 2 & 3 for the foreseeable future.  The reasons for this are that a) some users cannot upgrade pandoc and/or python; and b) supporting all versions tends to make pandoc-fignos more robust.

Developer notes are maintained in [README.developers].


What's New
----------

**New in 2.0.0:**  This version represents a major revision of pandoc-fignos.  While the interface is similar to that of the 1.x series, some users may encounter minor compatibility issues.

Warning messages are a new feature of pandoc-fignos.  The meta variable `fignos-warning-level` may be set to `0`, `1`, or `2` depending on the degree of warnings desired.  Warning level `1` (the default) will alert users to bad references, malformed attributes, and unknown meta variables.  Warning level `2` adds informational messages that should be helpful with debugging.  Level `0` turns all messages off.

Meta variable names have been updated.  Deprecated names have been removed, and new variables have been added.

The basic filter and library codes have been refactored and improved with a view toward maintainability.  While extensive tests have been performed, some problems may have slipped through unnoticed.  Bug reports should be submitted to our [Issues tracker].


*TeX/PDF:*

TeX codes produced by pandoc-fignos are massively improved.  The hacks used before were causing some users problems.  The new approach provides more flexibility and better compatibility with the LaTeX system.

Supporting TeX is now written to the `header-includes` meta data.  Users no longer need to include LaTeX commands in the `header-includes` to get basic pandoc-fignos functions to work.  Use `fignos-warning-level: 2` to see what pandoc-fignos adds to the `header-includes`.

A word of warning: Pandoc-fignos's additions to the `header-includes` are overridden when pandoc's `--include-in-header` option is used.  This is owing to a [design choice](https://github.com/jgm/pandoc/issues/3139) in pandoc.  Users may choose to deliberately override pandoc-fignos's `header-includes` by providing their own TeX through `--include-in-header`.  If a user needs to include other bits of TeX in this way, then they will need to do the same for the TeX that pandoc-fignos needs.

Finally, the `\label` tags are now installed where pandoc chooses, which is currently outside the `\caption` field.  Pandoc-fignos previously forced the `\label` to go inside `\caption`.


*Html/Epub:*

The figure is now enclosed in a `<div>` which contains the `id` and class `fignos`.  This change was made to facilitate styling.  The `id` was formerly contained in an anchor tag.

Epub support is generally improved.


----

**Footnotes**

<a name="footnote1">1</a>: Pandoc 2.4 [broke](https://github.com/jgm/pandoc/issues/5099) how references are parsed, and so is not supported.

<a name="footnote2">2</a>: The disabling modifier "!" is used instead of "-" because [pandoc unnecessarily drops minus signs] in front of references.

[pandoc unnecessarily drops minus signs]: https://github.com/jgm/pandoc/issues/2901
