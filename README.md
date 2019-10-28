
**New in 2.2.0:** Subfigures support.

**New in 2.1.1:** Warnings are given for duplicate reference targets.

**New in 2.0.0:** This is a major release which is easier to use at the cost of minor incompatibilities with previous versions.

[more...](#whats-new)


pandoc-fignos 2.2.0
===================

*pandoc-fignos* is a [pandoc] filter for numbering figures and their references when converting from markdown to other formats.  It is part of the [pandoc-xnos] filter suite.  LaTeX/pdf, html, and epub output have native support.  Native support for docx output is a work in progress.

Demonstration: Processing [demo3.md] with pandoc + pandoc-fignos gives numbered figures and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats.

This version of pandoc-fignos was tested using pandoc 1.15.2 - 2.7.3,<sup>[1](#footnote1)</sup> and may be used with linux, macOS, and Windows. Bug reports and feature requests may be posted on the project's [Issues tracker].  If you find pandoc-fignos useful, then please kindly give it a star [on GitHub].

See also: [pandoc-eqnos], [pandoc-tablenos], [pandoc-secnos] \
Other filters: [pandoc-comments], [pandoc-latex-extensions]

[pandoc]: http://pandoc.org/
[pandoc-xnos]: https://github.com/tomduck/pandoc-xnos
[Issues tracker]: https://github.com/tomduck/pandoc-fignos/issues
[on GitHub]:  https://github.com/tomduck/pandoc-fignos
[pandoc-eqnos]: https://github.com/tomduck/pandoc-eqnos
[pandoc-tablenos]: https://github.com/tomduck/pandoc-tablenos
[pandoc-secnos]: https://github.com/tomduck/pandoc-secnos
[pandoc-comments]: https://github.com/tomduck/pandoc-comments
[pandoc-latex-extensions]: https://github.com/tomduck/pandoc-latex-extensions


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

Pandoc-fignos may be installed using the shell command

    pip install pandoc-fignos --user

and upgraded by appending `--upgrade` to the above command.  Pip is a program that downloads and installs software from the Python Package Index, [PyPI].  It normally comes installed with a python distribution.<sup>[2](#footnote2)</sup>

Instructions for installing from source are given in [DEVELOPERS.md].

[python]: https://www.python.org/
[PyPI]: https://pypi.python.org/pypi
[DEVELOPERS.md]: DEVELOPERS.md


Usage
-----

Pandoc-fignos is activated by using the

    --filter pandoc-fignos

option with pandoc.  Alternatively, use

    --filter pandoc-xnos

to activate all of the filters in the [pandoc-xnos] suite (if installed).

Any use of `--filter pandoc-citeproc` or `--bibliography=FILE` should come *after* the `pandoc-fignos` or `pandoc-xnos` filter calls.


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

Curly braces protect a reference and are stripped from the output.

Demonstration: Processing [demo.md] with pandoc + pandoc-fignos gives numbered figures and references in [pdf], [tex], [html], [epub], [docx] and other formats.

[pandoc Issue #813]: https://github.com/jgm/pandoc/issues/813
[this post]: https://github.com/jgm/pandoc/issues/813#issuecomment-70423503
[@scaramouche1]: https://github.com/scaramouche1
[reference link]: http://pandoc.org/MANUAL.html#reference-links
[demo.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo.md
[pdf]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo.pdf
[tex]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo.tex
[html]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo.html
[epub]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo.epub
[docx]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo.docx


### Clever References ###

Writing markdown like

    See fig. @fig:id.

seems a bit redundant.  Pandoc-fignos supports "clever references" via single-character modifiers in front of a reference.  Users may write

     See +@fig:id.

to have the reference name (i.e., "fig.") automatically generated.  The above form is used mid-sentence; at the beginning of a sentence, use

     *@fig:id

instead.  If clever references are enabled by default (see [Customization](#customization), below), then users may disable it for a given reference using<sup>[3](#footnote3)</sup>

    !@fig:id

Demonstration: Processing [demo2.md] with pandoc + pandoc-fignos gives numbered figures and references in [pdf][pdf2], [tex][tex2], [html][html2], [epub][epub2], [docx][docx2] and other formats.

Note: When using `*@fig:id` and emphasis (e.g., `*italics*`) in the same sentence, the `*` in the clever reference must be backslash-escaped; i.e., `\*@fig:id`.

[demo2.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo2.md
[pdf2]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo2.pdf
[tex2]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo2.tex
[html2]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo2.html
[epub2]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo2.epub
[docx2]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo2.docx


### Tagged Figures ###

The figure number may be overridden by placing a tag in the figure's attributes block:

    ![Caption.](image.png){#fig:id tag="B.1"}

The tag may be arbitrary text, or an inline equation such as `$\text{B.1}'$`.  Mixtures of the two are not currently supported.


### Disabling Links ###

To disable a link on a reference, set `nolink=True` in the reference's attributes:

    @fig:id{nolink=True}


### Subfigures ###

Pandoc does not provide syntactical support for subfigures.  However, subfigures of arbitrary complexity assembled using the native capabilities of each output format may still be referenced.

*LaTeX/pdf* subfigures may be coded and referenced as shown in [demo4.md].  Processing with pandoc + pandoc-fignos gives [demo4.pdf].  This technique uses capabilities provided by the [subcaption] package.  "Bad reference" warnings involving subfigures may be ignored when using this approach.

*Html/epub* subfigures may be coded and referenced as shown in [demo5.md].  Processing with pandoc + pandoc-fignos gives [demo5.html].  This technique uses pandoc [divs].  Divs may be nested and styled as required with css.  Note that pandoc requires figures to be in their own paragraph (i.e., with a blank line above and below).

[demo4.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo4.md
[demo4.pdf]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo4.pdf
[subcaption]: 
[demo5.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo5.md
[demo5.html]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo5.html
[divs]: https://pandoc.org/MANUAL.html#divs-and-spans


Customization
-------------

Pandoc-fignos may be customized by setting variables in the [metadata block] or on the command line (using `-M KEY=VAL`).  The following variables are supported:

  * `fignos-warning-level` or `xnos-warning-level` - Set to `0` for
    no warnings, `1` for critical warnings, or `2` (default) for
    all warnings.  Warning level 2 should be used when
    troubleshooting.

  * `fignos-cleveref` or `xnos-cleveref` - Set to `True` to assume "+"
    clever references by default;

  * `xnos-capitalise` - Capitalises the names of "+" clever
    references (e.g., change from "fig." to "Fig.");

  * `fignos-plus-name` - Sets the name of a "+" clever reference
    (e.g., change it from "fig." to "figure").  Settings here take
    precedence over `xnos-capitalise`;

  * `fignos-star-name` - Sets the name of a "*" clever reference
    (e.g., change it from "Figure" to "Fig.");

  * `fignos-caption-name` - Sets the name at the beginning of a
    caption (e.g., change it from "Figure to "Fig." or "图");

  * `fignos-caption-separator` or `xnos-caption-separator` - Sets 
    the caption separator (e.g., the colon in "Figure 1:") to
    something else.  It must be one of `none`, `colon`,
    `period`, `space`, `quad`, or `newline`; and

  * `fignos-number-by-section` or `xnos-number-by-section` - Set to
    `True` to number figures by section (e.g., Fig. 1.1, 1.2, etc in
    Section 1, and Fig 2.1, 2.2, etc in Section 2).  For LaTeX/pdf,
    html, and epub output, this feature should be used together with
    pandoc's `--number-sections`
    [option](https://pandoc.org/MANUAL.html#option--number-sections)
    enabled.  For docx, use [docx custom styles] instead.

    This option should not be set for numbering by chapter in
    LaTeX/pdf book document classes.

  * `xnos-number-offset` - Set to an integer to offset the section
    numbers when numbering figures by section.  For html and epub
    output, this feature should be used together with pandoc's
    `--number-offset`
    [option](https://pandoc.org/MANUAL.html#option--number-sections)
    set to the same integer value.  For LaTeX/PDF, this option
    offsets the actual section numbers as required.


Note that variables beginning with `fignos-` apply to only pandoc-fignos, whereas variables beginning with `xnos-` apply to all of the pandoc-fignos/eqnos/tablenos/secnos filters.

Demonstration: Processing [demo3.md] with pandoc + pandoc-fignos gives numbered figures and references in [pdf][pdf3], [tex][tex3], [html][html3], [epub][epub3], [docx][docx3] and other formats.

[metadata block]: http://pandoc.org/README.html#extension-yaml_metadata_block
[docx custom styles]: https://pandoc.org/MANUAL.html#custom-styles
[demo3.md]: https://raw.githubusercontent.com/tomduck/pandoc-fignos/master/demos/demo3.md
[pdf3]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo3.pdf
[tex3]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo3.tex
[html3]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo3.html
[epub3]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo3.epub
[docx3]: https://raw.githack.com/tomduck/pandoc-fignos/demos/demo3.docx


Technical Details
-----------------

### TeX/pdf Output ###

During processing, pandoc-fignos inserts packages and supporting TeX into the `header-includes` metadata field.  To see what is inserted, set the `fignos-warning-level` meta variable to `2`.  Note that any use of pandoc's `--include-in-header` option [overrides](https://github.com/jgm/pandoc/issues/3139) all `header-includes`.

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
    clever references);
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

The figure and its caption are wrapped in a `<div></div>` with an `id` for linking and with class `fignos` to allow for css styling.


### Docx Output ###

Docx OOXML output is under development and subject to change.  Native capabilities will be used wherever possible.


Getting Help
------------

If you have any difficulties with pandoc-fignos, or would like to see a new feature, then please submit a report to our [Issues tracker].


Development
-----------

Pandoc-fignos will continue to support pandoc 1.15-onward and python 2 & 3 for the foreseeable future.  The reasons for this are that a) some users cannot upgrade pandoc and/or python; and b) supporting all versions tends to make pandoc-fignos more robust.

Developer notes are maintained in [DEVELOPERS.md].


What's New
----------

**New in 2.2.0:** Added html/epub subfigures support.

**New in 2.1.2:** LaTeX subfigures support.  Documentation is provided to show how to reference LaTeX subfigures.  No changes to existing code were required.

**New in 2.1.1:** Warnings are given for duplicate reference targets.

**New in 2.0.0:**  This version represents a major revision of pandoc-fignos.  While the interface is similar to that of the 1.x series, some users may encounter minor compatibility issues.

Warning messages are a new feature of pandoc-fignos.  The meta variable `fignos-warning-level` may be set to `0`, `1`, or `2` depending on the degree of warnings desired.  Warning level `1` will alert users to bad references, malformed attributes, and unknown meta variables.  Warning level `2` (the default) adds informational messages that should be helpful with debugging.  Level `0` turns all messages off.

Meta variable names have been updated.  Deprecated names have been removed, and new variables have been added.  Note in particular that the `fignos-number-sections` and `xnos-number-sections` variables have been renamed to `fignos-number-by-section` and `xnos-number-by-section`, respectively.

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

<a name="footnote2">2</a>: Anaconda users may be tempted to use `conda` instead.  This is not advised.  The packages distributed on the Anaconda cloud are unofficial, are not posted by me, and in some cases are ancient.  Some tips on using `pip` in a `conda` environment may be found [here](https://www.anaconda.com/using-pip-in-a-conda-environment/).

<a name="footnote3">3</a>: The disabling modifier "!" is used instead of "-" because [pandoc unnecessarily drops minus signs] in front of references.

[pandoc unnecessarily drops minus signs]: https://github.com/jgm/pandoc/issues/2901
