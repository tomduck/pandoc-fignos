#! /usr/bin/env python

"""pandoc-fignos: a pandoc filter that inserts figure nos. and refs."""


__version__ = '2.4.0'


# Copyright 2015-2020 Thomas J. Duck.
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# OVERVIEW
#
# The basic idea is to scan the document twice in order to:
#
#   1. Insert text for the figure number in each figure caption.
#      For LaTeX, insert \label{...} instead.  The figure ids
#      and associated figure numbers are stored in the global
#      target tracker.
#
#   2. Replace each reference with a figure number.  For LaTeX,
#      replace with \ref{...} instead.
#
# This is followed by injecting header code as needed for certain output
# formats.


# pylint: disable=invalid-name

import sys
import re
import functools
import argparse
import json
import copy
import textwrap
import uuid

from pandocfilters import walk
from pandocfilters import Image, Div
from pandocfilters import Math, Str, Space, Para, RawBlock, RawInline
from pandocfilters import Span

import pandocxnos
from pandocxnos import PandocAttributes
from pandocxnos import STRTYPES, STDIN, STDOUT, STDERR
from pandocxnos import NBSP
from pandocxnos import elt, check_bool, get_meta, extract_attrs
from pandocxnos import repair_refs, process_refs_factory, replace_refs_factory
from pandocxnos import attach_attrs_factory, detach_attrs_factory
from pandocxnos import insert_secnos_factory, delete_secnos_factory
from pandocxnos import version

if sys.version_info > (3,):
    from urllib.request import unquote
else:
    from urllib import unquote  # pylint: disable=no-name-in-module

# Compiled regular expression for matching labels
LABEL_PATTERN = re.compile(r'(fig:[\w/-]*)')

# Meta variables; may be reset elsewhere
captionname = 'Figure'  # The caption name
separator = 'colon'     # The caption separator
cleveref = False        # Flags that clever references should be used
capitalise = False      # Flags that plusname should be capitalised
plusname = ['fig.', 'figs.']      # Sets names for mid-sentence references
starname = ['Figure', 'Figures']  # Sets names for references at sentence start
numbersections = False  # Flags that figures should be numbered by section
secoffset = 0           # Section number offset
warninglevel = 2        # 0 - no warnings; 1 - some warnings; 2 - all warnings

# Processing state variables
cursec = None  # Current section
Ntargets = 0   # Number of targets in current section (or document)
targets = {}   # Global targets tracker

# Processing flags
captionname_changed = False     # Flags the caption name changed
separator_changed = False       # Flags the caption separator changed
plusname_changed = False        # Flags that the plus name changed
starname_changed = False        # Flags that the star name changed
has_unnumbered_figures = False  # Flags unnumbered figures were found
has_tagged_figures = False      # Flags a tagged figure was found

PANDOCVERSION = None


# Actions --------------------------------------------------------------------

def _extract_attrs(x, n):
    """Extracts attributes for an image in the element list `x`.  The
    attributes begin at index `n`.  Extracted elements are deleted
    from the list.
    """
    try:  #  Try the standard call from pandocxnos first
        return extract_attrs(x, n)

    except (ValueError, IndexError):

        if version(PANDOCVERSION) < version('1.16'):
            # Look for attributes attached to the image path, as occurs with
            # image references for pandoc < 1.16 (pandoc-fignos Issue #14).
            # See http://pandoc.org/MANUAL.html#images for the syntax.
            # Note: This code does not handle the "optional title" for
            # image references (search for link_attributes in pandoc's docs).
            assert x[n-1]['t'] == 'Image'
            image = x[n-1]
            s = image['c'][-1][0]
            if '%20%7B' in s:
                path = s[:s.index('%20%7B')]
                attrstr = unquote(s[s.index('%7B'):])
                image['c'][-1][0] = path  # Remove attr string from the path
                return PandocAttributes(attrstr.strip(), 'markdown')
        raise


def _process_figure(key, value, fmt):
    """Processes a figure.  Returns a dict containing figure properties.

    Parameters:

      key - 'Para' (for a normal figure) or 'Div'
      value - the content of the figure
      fmt - the output format ('tex', 'html', ...)
    """

    # pylint: disable=global-statement
    global cursec    # Current section being processed
    global Ntargets  # Number of targets in current section (or document)
    global has_unnumbered_figures  # Flags that unnumbered figures were found

    # Initialize the return value
    fig = {'is_unnumbered': False,
           'is_unreferenceable': False,
           'is_tagged': False}

    # Bail out if there are no attributes
    if key == 'Para' and len(value[0]['c']) == 2:
        has_unnumbered_figures = True
        fig.update({'is_unnumbered': True, 'is_unreferenceable': True})
        return fig

    # Parse the figure
    attrs = fig['attrs'] = \
      PandocAttributes(value[0]['c'][0] if key == 'Para' else value[0],
                       'pandoc')
    fig['caption'] = value[0]['c'][1] if key == 'Para' else None

    # Bail out if the label does not conform to expectations
    if not LABEL_PATTERN.match(attrs.id):
        has_unnumbered_figures = True
        fig.update({'is_unnumbered': True, 'is_unreferenceable': True})
        return fig

    # Identify unreferenceable figures
    if attrs.id == 'fig:':
        attrs.id += str(uuid.uuid4())
        fig['is_unreferenceable'] = True

    # Update the current section number
    if attrs['secno'] != cursec:  # The section number changed
        cursec = attrs['secno']   # Update the global section tracker
        if numbersections:
            Ntargets = 0          # Resets the global target counter

    # Increment the targets counter
    if 'tag' not in attrs:
        Ntargets += 1

    # Pandoc's --number-sections supports section numbering latex/pdf, html,
    # epub, and docx
    if numbersections:
        # Latex/pdf supports equation numbers by section natively.  For the
        # other formats we must hard-code in figure numbers by section as
        # tags.
        if fmt in ['html', 'html4', 'html5', 'epub', 'epub2', 'epub3',
                   'docx'] and \
          'tag' not in attrs:
            attrs['tag'] = str(cursec+secoffset) + '.' + str(Ntargets)

    # Update the global targets tracker
    fig['is_tagged'] = 'tag' in attrs
    if fig['is_tagged']:  # ... then save the tag
        # Remove any surrounding quotes
        if attrs['tag'][0] == '"' and attrs['tag'][-1] == '"':
            attrs['tag'] = attrs['tag'].strip('"')
        elif attrs['tag'][0] == "'" and attrs['tag'][-1] == "'":
            attrs['tag'] = attrs['tag'].strip("'")
        targets[attrs.id] = pandocxnos.Target(attrs['tag'], cursec,
                                              attrs.id in targets)
    else:  # ... then save the figure number
        targets[attrs.id] = pandocxnos.Target(Ntargets, cursec,
                                              attrs.id in targets)

    return fig

def _adjust_caption(fmt, fig, value):
    """Adjusts the caption."""
    attrs, caption = fig['attrs'], fig['caption']
    if fmt in ['latex', 'beamer']:  # Append a \label if this is referenceable
        if version(PANDOCVERSION) < version('1.17') and \
          not fig['is_unreferenceable']:
            # pandoc >= 1.17 installs \label for us
            value[0]['c'][1] += \
              [RawInline('tex', r'\protect\label{%s}'%attrs.id)]
    else:  # Hard-code in the caption name and number/tag
        if fig['is_unnumbered']:
            return
        sep = {'none':'', 'colon':':', 'period':'.', 'space':' ',
               'quad':u'\u2000', 'newline':'\n'}[separator]

        num = targets[attrs.id].num
        if isinstance(num, int):  # Numbered target
            if fmt in ['html', 'html4', 'html5', 'epub', 'epub2', 'epub3']:
                value[0]['c'][1] = [RawInline('html', r'<span>'),
                                    Str(captionname+NBSP),
                                    Str('%d%s' % (num, sep)),
                                    RawInline('html', r'</span>')]
            else:
                value[0]['c'][1] = [Str(captionname+NBSP),
                                    Str('%d%s' % (num, sep))]
        else:  # Tagged target
            if num.startswith('$') and num.endswith('$'):  # Math
                math = num.replace(' ', r'\ ')[1:-1]
                els = [Math({"t":"InlineMath", "c":[]}, math), Str(sep)]
            else:  # Text
                els = [Str(num+sep)]
            if fmt in ['html', 'html4', 'html5', 'epub', 'epub2', 'epub3']:
                value[0]['c'][1] = \
                  [RawInline('html', r'<span>'), Str(captionname+NBSP)] + \
                  els + [RawInline('html', r'</span>')]
            else:
                value[0]['c'][1] = [Str(captionname+NBSP)] + els
        value[0]['c'][1] += [Space()] + list(caption)

def _add_markup(fmt, fig, value):
    """Adds markup to the output."""

    # pylint: disable=global-statement
    global has_tagged_figures  # Flags a tagged figure was found

    if fig['is_unnumbered']:
        if fmt in ['latex', 'beamer']:
            # Use the no-prefix-figure-caption environment
            return [RawBlock('tex', r'\begin{fignos:no-prefix-figure-caption}'),
                    Para(value),
                    RawBlock('tex', r'\end{fignos:no-prefix-figure-caption}')]
        return None  # Nothing to do

    attrs = fig['attrs']
    ret = None

    if fmt in ['latex', 'beamer']:
        if fig['is_tagged']:  # A figure cannot be tagged if it is unnumbered
            # Use the tagged-figure environment
            has_tagged_figures = True
            ret = [RawBlock('tex', r'\begin{fignos:tagged-figure}[%s]' % \
                            str(targets[attrs.id].num)),
                   Para(value),
                   RawBlock('tex', r'\end{fignos:tagged-figure}')]
    elif fmt in ('html', 'html4', 'html5', 'epub', 'epub2', 'epub3'):
        if LABEL_PATTERN.match(attrs.id):
            pre = RawBlock('html', '<div id="%s" class="fignos">'%attrs.id)
            post = RawBlock('html', '</div>')
            ret = [pre, Para(value), post]
            # Eliminate the id from the Image
            attrs.id = ''
            value[0]['c'][0] = attrs.list
    elif fmt == 'docx':
        # As per http://officeopenxml.com/WPhyperlink.php
        bookmarkstart = \
          RawBlock('openxml',
                   '<w:bookmarkStart w:id="0" w:name="%s"/>'
                   %attrs.id)
        bookmarkend = \
          RawBlock('openxml', '<w:bookmarkEnd w:id="0"/>')
        ret = [bookmarkstart, Para(value), bookmarkend]
    return ret

def process_figures(key, value, fmt, meta):  # pylint: disable=unused-argument
    """Processes the figures."""

    # Process figures wrapped in Para elements
    if key == 'Para' and len(value) == 1 and \
      value[0]['t'] == 'Image' and value[0]['c'][-1][1].startswith('fig:'):

        # Process the figure and add markup
        fig = _process_figure(key, value, fmt)
        if 'attrs' in fig:
            _adjust_caption(fmt, fig, value)
        return _add_markup(fmt, fig, value)

    if key == 'Div' and LABEL_PATTERN.match(value[0][0]):
        fig = _process_figure(key, value, fmt)

    return None


# TeX blocks -----------------------------------------------------------------

# Define an environment that disables figure caption prefixes.  Counters
# must be saved and later restored.  The \thefigure and \theHfigure counter
# must be set to something unique so that duplicate internal names are avoided
# (see Sect. 3.2 of
# http://ctan.mirror.rafal.ca/macros/latex/contrib/hyperref/doc/manual.html).
NO_PREFIX_CAPTION_ENV_TEX = r"""
%% pandoc-fignos: environment to disable figure caption prefixes
\makeatletter
\newcounter{figno}
\newenvironment{fignos:no-prefix-figure-caption}{
  \caption@ifcompatibility{}{
    \let\oldthefigure\thefigure
    \let\oldtheHfigure\theHfigure
    \renewcommand{\thefigure}{figno:\thefigno}
    \renewcommand{\theHfigure}{figno:\thefigno}
    \stepcounter{figno}
    \captionsetup{labelformat=empty}
  }
}{
  \caption@ifcompatibility{}{
    \captionsetup{labelformat=default}
    \let\thefigure\oldthefigure
    \let\theHfigure\oldtheHfigure
    \addtocounter{figure}{-1}
  }
}
\makeatother
"""

# Define an environment for tagged figures
TAGGED_FIGURE_ENV_TEX = r"""
%% pandoc-fignos: environment for tagged figures
\newenvironment{fignos:tagged-figure}[1][]{
  \let\oldthefigure\thefigure
  \let\oldtheHfigure\theHfigure
  \renewcommand{\thefigure}{#1}
  \renewcommand{\theHfigure}{#1}
}{
  \let\thefigure\oldthefigure
  \let\theHfigure\oldtheHfigure
  \addtocounter{figure}{-1}
}
"""

# Reset the caption name; i.e. change "Figure" at the beginning of a caption
# to something else.
CAPTION_NAME_TEX = r"""
%% pandoc-fignos: change the caption name
\renewcommand{\figurename}{%s}
"""

# Reset the label separator; i.e. change the colon after "Figure 1:" to
# something else.
CAPTION_SEPARATOR_TEX = r"""
%% pandoc-fignos: change the caption separator
\captionsetup[figure]{labelsep=%s}
"""

# Number figures by section
NUMBER_BY_SECTION_TEX = r"""
%% pandoc-fignos: number figures by section
\numberwithin{figure}{section}
"""

# Section number offset
SECOFFSET_TEX = r"""
%% pandoc-fignos: section number offset
\setcounter{section}{%s}
"""


# Main program ---------------------------------------------------------------

# pylint: disable=too-many-branches,too-many-statements
def process(meta):
    """Saves metadata fields in global variables and returns a few
    computed fields."""

    # pylint: disable=global-statement
    global captionname     # The caption name
    global separator       # The caption separator
    global cleveref        # Flags that clever references should be used
    global capitalise      # Flags that plusname should be capitalised
    global plusname        # Sets names for mid-sentence references
    global starname        # Sets names for references at sentence start
    global numbersections  # Flags that sections should be numbered by section
    global secoffset       # Section number offset
    global warninglevel    # 0 - no warnings; 1 - some; 2 - all
    global captionname_changed  # Flags the caption name changed
    global separator_changed    # Flags the caption separator changed
    global plusname_changed     # Flags that the plus name changed
    global starname_changed     # Flags that the star name changed

    # Read in the metadata fields and do some checking

    for name in ['fignos-warning-level', 'xnos-warning-level']:
        if name in meta:
            warninglevel = int(get_meta(meta, name))
            pandocxnos.set_warning_level(warninglevel)
            break

    metanames = ['fignos-warning-level', 'xnos-warning-level',
                 'fignos-caption-name',
                 'fignos-caption-separator', 'xnos-caption-separator',
                 'fignos-cleveref', 'xnos-cleveref',
                 'xnos-capitalise', 'xnos-capitalize',
                 'fignos-plus-name', 'fignos-star-name',
                 'fignos-number-by-section', 'xnos-number-by-section',
                 'xnos-number-offset']

    if warninglevel:
        for name in meta:
            if (name.startswith('fignos') or name.startswith('xnos')) and \
              name not in metanames:
                msg = textwrap.dedent("""
                          pandoc-fignos: unknown meta variable "%s"
                      """ % name)
                STDERR.write(msg)

    if 'fignos-caption-name' in meta:
        old_captionname = captionname
        captionname = get_meta(meta, 'fignos-caption-name')
        captionname_changed = captionname != old_captionname
        assert isinstance(captionname, STRTYPES)

    for name in ['fignos-caption-separator', 'xnos-caption-separator']:
        if name in meta:
            old_separator = separator
            separator = get_meta(meta, name)
            if separator not in \
              ['none', 'colon', 'period', 'space', 'quad', 'newline']:
                msg = textwrap.dedent("""
                          pandoc-fignos: caption separator must be one of
                          none, colon, period, space, quad, or newline.
                      """ % name)
                STDERR.write(msg)
                continue
            separator_changed = separator != old_separator
            break

    for name in ['fignos-cleveref', 'xnos-cleveref']:
        # 'xnos-cleveref' enables cleveref in all 3 of fignos/eqnos/tablenos
        if name in meta:
            cleveref = check_bool(get_meta(meta, name))
            break

    for name in ['xnos-capitalise', 'xnos-capitalize']:
        # 'xnos-capitalise' enables capitalise in all 3 of
        # fignos/eqnos/tablenos.  Since this uses an option in the caption
        # package, it is not possible to select between the three (use
        # 'fignos-plus-name' instead.  'xnos-capitalize' is an alternative
        # spelling
        if name in meta:
            capitalise = check_bool(get_meta(meta, name))
            break

    if 'fignos-plus-name' in meta:
        tmp = get_meta(meta, 'fignos-plus-name')
        old_plusname = copy.deepcopy(plusname)
        if isinstance(tmp, list):  # The singular and plural forms were given
            plusname = tmp
        else:  # Only the singular form was given
            plusname[0] = tmp
        plusname_changed = plusname != old_plusname
        assert len(plusname) == 2
        for name in plusname:
            assert isinstance(name, STRTYPES)
        if plusname_changed:
            starname = [name.title() for name in plusname]

    if 'fignos-star-name' in meta:
        tmp = get_meta(meta, 'fignos-star-name')
        old_starname = copy.deepcopy(starname)
        if isinstance(tmp, list):
            starname = tmp
        else:
            starname[0] = tmp
        starname_changed = starname != old_starname
        assert len(starname) == 2
        for name in starname:
            assert isinstance(name, STRTYPES)

    for name in ['fignos-number-by-section', 'xnos-number-by-section']:
        if name in meta:
            numbersections = check_bool(get_meta(meta, name))
            break

    if 'xnos-number-offset' in meta:
        secoffset = int(get_meta(meta, 'xnos-number-offset'))

def add_tex(meta):
    """Adds tex to the meta data."""

    # pylint: disable=too-many-boolean-expressions
    warnings = warninglevel == 2 and targets and \
      (pandocxnos.cleveref_required() or has_unnumbered_figures or
       plusname_changed or starname_changed or has_tagged_figures or
       captionname_changed or numbersections or secoffset)
    if warnings:
        msg = textwrap.dedent("""\
                  pandoc-fignos: Wrote the following blocks to
                  header-includes.  If you use pandoc's
                  --include-in-header option then you will need to
                  manually include these yourself.
              """)
        STDERR.write('\n')
        STDERR.write(textwrap.fill(msg))
        STDERR.write('\n')

    # Update the header-includes metadata.  Pandoc's
    # --include-in-header option will override anything we do here.  This
    # is a known issue and is owing to a design decision in pandoc.
    # See https://github.com/jgm/pandoc/issues/3139.

    if pandocxnos.cleveref_required() and targets:
        tex = """
            %%%% pandoc-fignos: required package
            \\usepackage%s{cleveref}
        """ % ('[capitalise]' if capitalise else '')
        pandocxnos.add_to_header_includes(
            meta, 'tex', tex, regex=r'\\usepackage(\[[\w\s,]*\])?\{cleveref\}')

    if has_unnumbered_figures or (separator_changed and targets):
        tex = """
            %%%% pandoc-fignos: required package
            \\usepackage{caption}
        """
        pandocxnos.add_to_header_includes(
            meta, 'tex', tex, regex=r'\\usepackage(\[[\w\s,]*\])?\{caption\}')

    if plusname_changed and targets:
        tex = """
            %%%% pandoc-fignos: change cref names
            \\crefname{figure}{%s}{%s}
        """ % (plusname[0], plusname[1])
        pandocxnos.add_to_header_includes(meta, 'tex', tex)

    if starname_changed and targets:
        tex = """
            %%%% pandoc-fignos: change Cref names
            \\Crefname{figure}{%s}{%s}
        """ % (starname[0], starname[1])
        pandocxnos.add_to_header_includes(meta, 'tex', tex)

    if has_unnumbered_figures:
        pandocxnos.add_to_header_includes(
            meta, 'tex', NO_PREFIX_CAPTION_ENV_TEX)

    if has_tagged_figures and targets:
        pandocxnos.add_to_header_includes(meta, 'tex', TAGGED_FIGURE_ENV_TEX)

    if captionname_changed and targets:
        pandocxnos.add_to_header_includes(
            meta, 'tex', CAPTION_NAME_TEX % captionname)

    if separator_changed and targets:
        pandocxnos.add_to_header_includes(
            meta, 'tex', CAPTION_SEPARATOR_TEX % separator)

    if numbersections and targets:
        pandocxnos.add_to_header_includes(meta, 'tex', NUMBER_BY_SECTION_TEX)

    if secoffset and targets:
        pandocxnos.add_to_header_includes(
            meta, 'tex', SECOFFSET_TEX % secoffset,
            regex=r'\\setcounter\{section\}')

    if warnings:
        STDERR.write('\n')

# pylint: disable=too-many-locals, unused-argument
def main(stdin=STDIN, stdout=STDOUT, stderr=STDERR):
    """Filters the document AST."""

    # pylint: disable=global-statement
    global PANDOCVERSION
    global Image

    # Read the command-line arguments
    parser = argparse.ArgumentParser(\
      description='Pandoc figure numbers filter.')
    parser.add_argument(\
      '--version', action='version',
      version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('fmt')
    parser.add_argument('--pandocversion', help='The pandoc version.')
    args = parser.parse_args()

    # Get the output format and document
    fmt = args.fmt
    doc = json.loads(stdin.read())

    # Initialize pandocxnos
    PANDOCVERSION = pandocxnos.init(args.pandocversion, doc)

    # Element primitives
    if version(PANDOCVERSION) < version('1.16'):
        Image = elt('Image', 2)

    # Chop up the doc
    meta = doc['meta'] if version(PANDOCVERSION) >= version('1.18') \
      else doc[0]['unMeta']
    blocks = doc['blocks'] if version(PANDOCVERSION) >= version('1.18') \
      else doc[1:]

    # Process the metadata variables
    process(meta)

    # First pass
    replace = version(PANDOCVERSION) >= version('1.16')
    attach_attrs_image = attach_attrs_factory(Image,
                                              extract_attrs=_extract_attrs,
                                              replace=replace)
    detach_attrs_image = detach_attrs_factory(Image)
    insert_secnos_img = insert_secnos_factory(Image)
    delete_secnos_img = delete_secnos_factory(Image)
    insert_secnos_div = insert_secnos_factory(Div)
    delete_secnos_div = delete_secnos_factory(Div)
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [attach_attrs_image,
                                insert_secnos_img, insert_secnos_div,
                                process_figures,
                                delete_secnos_img, delete_secnos_div,
                                detach_attrs_image], blocks)

    # Second pass
    process_refs = process_refs_factory(LABEL_PATTERN, targets.keys())
    replace_refs = replace_refs_factory(targets, cleveref, False,
                                        plusname if not capitalise \
                                        or plusname_changed else
                                        [name.title() for name in plusname],
                                        starname)
    attach_attrs_span = attach_attrs_factory(Span, replace=True)
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [repair_refs, process_refs, replace_refs,
                                attach_attrs_span],
                               altered)

    if fmt in ['latex', 'beamer']:
        add_tex(meta)

    # Update the doc
    if version(PANDOCVERSION) >= version('1.18'):
        doc['blocks'] = altered
    else:
        doc = doc[:1] + altered

    # Dump the results
    json.dump(doc, stdout)

    # Flush stdout
    stdout.flush()

if __name__ == '__main__':
    main()
