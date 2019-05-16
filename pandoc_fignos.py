#! /usr/bin/env python

"""pandoc-fignos: a pandoc filter that inserts figure nos. and refs."""

# Copyright 2015-2019 Thomas J. Duck.
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
#      references tracker.
#
#   2. Replace each reference with a figure number.  For LaTeX,
#      replace with \ref{...} instead.

# pylint: disable=invalid-name

import sys
import re
import functools
import argparse
import json
import uuid

from pandocfilters import walk
from pandocfilters import Image, Math, Str, Space, Para, RawBlock, RawInline
from pandocfilters import Span

import pandocxnos
from pandocxnos import PandocAttributes
from pandocxnos import STRTYPES, STDIN, STDOUT
from pandocxnos import elt, check_bool, get_meta, extract_attrs
from pandocxnos import repair_refs, process_refs_factory, replace_refs_factory
from pandocxnos import attach_attrs_factory, detach_attrs_factory
from pandocxnos import insert_secnos_factory, delete_secnos_factory
from pandocxnos import insert_rawblocks_factory

if sys.version_info > (3,):
    from urllib.request import unquote  # pylint: disable=no-name-in-module
else:
    from urllib import unquote  # pylint: disable=no-name-in-module


# Read the command-line arguments
parser = argparse.ArgumentParser(description='Pandoc figure numbers filter.')
parser.add_argument('fmt')
parser.add_argument('--pandocversion', help='The pandoc version.')
args = parser.parse_args()

# Pattern for matching labels
LABEL_PATTERN = re.compile(r'(fig:[\w/-]*)')

Nreferences = 0        # Global references counter
references = {}        # Global references tracker
unreferenceable = []   # List of labels that are unreferenceable

# Meta variables; may be reset elsewhere
captionname = 'Figure'            # Used with \figurename
plusname = ['fig.', 'figs.']      # Used with \cref
starname = ['Figure', 'Figures']  # Used with \Cref

use_cleveref_default = False      # Default setting for clever referencing
capitalize = False                # Default setting for capitalizing plusname

# Flag for unnumbered figures
has_unnumbered_figures = False

# Variables for tracking section numbers
numbersections = False
cursec = None

PANDOCVERSION = None


# Actions --------------------------------------------------------------------

def _extract_attrs(x, n):
    """Extracts attributes for an image.  n is the index where the
    attributes begin.  Extracted elements are deleted from the element
    list x.  Attrs are returned in pandoc format.
    """
    try:
        return extract_attrs(x, n)

    except (ValueError, IndexError):

        if PANDOCVERSION < '1.16':
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
                attrs = unquote(s[s.index('%7B'):])
                image['c'][-1][0] = path  # Remove attr string from the path
                return PandocAttributes(attrs.strip(), 'markdown').to_pandoc()
        raise


# pylint: disable=too-many-branches
def _process_figure(value, fmt):
    """Processes the figure.  Returns a dict containing figure properties."""

    # pylint: disable=global-statement
    global Nreferences             # Global references counter
    global has_unnumbered_figures  # Flags unnumbered figures were found
    global cursec                  # Current section

    # Parse the image
    attrs, caption = value[0]['c'][:2]

    # Initialize the return value
    fig = {'is_unnumbered': False,
           'is_unreferenceable': False,
           'is_tagged': False,
           'attrs': attrs}

    # Bail out if the label does not conform
    if not LABEL_PATTERN.match(attrs[0]):
        has_unnumbered_figures = True
        fig['is_unnumbered'] = True
        fig['is_unreferenceable'] = True
        return fig

    # Process unreferenceable figures
    if attrs[0] == 'fig:': # Make up a unique description
        attrs[0] = attrs[0] + str(uuid.uuid4())
        fig['is_unreferenceable'] = True
        unreferenceable.append(attrs[0])

    # For html, hard-code in the section numbers as tags
    kvs = PandocAttributes(attrs, 'pandoc').kvs
    if numbersections and fmt in ['html', 'html5'] and 'tag' not in kvs:
        if kvs['secno'] != cursec:
            cursec = kvs['secno']
            Nreferences = 1
        kvs['tag'] = cursec + '.' + str(Nreferences)
        Nreferences += 1

    # Save to the global references tracker
    fig['is_tagged'] = 'tag' in kvs
    if fig['is_tagged']:
        # Remove any surrounding quotes
        if kvs['tag'][0] == '"' and kvs['tag'][-1] == '"':
            kvs['tag'] = kvs['tag'].strip('"')
        elif kvs['tag'][0] == "'" and kvs['tag'][-1] == "'":
            kvs['tag'] = kvs['tag'].strip("'")
        references[attrs[0]] = kvs['tag']
    else:
        Nreferences += 1
        references[attrs[0]] = Nreferences

    # Adjust caption depending on the output format
    if fmt in ['latex', 'beamer']:  # Append a \label if this is referenceable
        if not fig['is_unreferenceable']:
            value[0]['c'][1] += [RawInline('tex', r'\label{%s}'%attrs[0])]
    else:  # Hard-code in the caption name and number/tag
        if isinstance(references[attrs[0]], int):  # Numbered reference
            value[0]['c'][1] = [RawInline('html', r'<span>'),
                                Str(captionname), Space(),
                                Str('%d:'%references[attrs[0]]),
                                RawInline('html', r'</span>')] \
                if fmt in ['html', 'html5'] else \
                [Str(captionname), Space(), Str('%d:'%references[attrs[0]])]
            value[0]['c'][1] += [Space()] + list(caption)
        else:  # Tagged reference
            assert isinstance(references[attrs[0]], STRTYPES)
            text = references[attrs[0]]
            if text.startswith('$') and text.endswith('$'):  # Math
                math = text.replace(' ', r'\ ')[1:-1]
                els = [Math({"t":"InlineMath", "c":[]}, math), Str(':')]
            else:  # Text
                els = [Str(text+':')]
            value[0]['c'][1] = \
                [RawInline('html', r'<span>'), Str(captionname), Space()] + \
                els + [RawInline('html', r'</span>')] \
                if fmt in ['html', 'html5'] else \
                [Str(captionname), Space()] + els
            value[0]['c'][1] += [Space()] + list(caption)

    return fig

# pylint: disable=too-many-branches, too-many-return-statements
def process_figures(key, value, fmt, meta): # pylint: disable=unused-argument
    """Processes the figures."""

    global has_unnumbered_figures  # pylint: disable=global-statement

    # Process figures wrapped in Para elements
    if key == 'Para' and len(value) == 1 and \
      value[0]['t'] == 'Image' and value[0]['c'][-1][1].startswith('fig:'):

        # Inspect the image
        if len(value[0]['c']) == 2:  # Unattributed, bail out
            has_unnumbered_figures = True
            if fmt == 'latex':
                return [RawBlock('tex', r'\begin{no-prefix-figure-caption}'),
                        Para(value),
                        RawBlock('tex', r'\end{no-prefix-figure-caption}')]
            return None

        # Process the figure
        fig = _process_figure(value, fmt)

        # Context-dependent output
        attrs = fig['attrs']
        if fig['is_unnumbered']:  # Unnumbered is also unreferenceable
            if fmt == 'latex':
                return [
                    RawBlock('tex', r'\begin{no-prefix-figure-caption}'),
                    Para(value),
                    RawBlock('tex', r'\end{no-prefix-figure-caption}')]
        elif fmt in ['latex', 'beamer']:
            key = attrs[0]
            if PANDOCVERSION >= '1.17':
                # Remove id from the image attributes.  It is incorrectly
                # handled by pandoc's TeX writer for these versions.
                if LABEL_PATTERN.match(attrs[0]):
                    attrs[0] = ''
            if fig['is_tagged']:  # Code in the tags
                tex = '\n'.join([r'\let\oldthefigure=\thefigure',
                                 r'\renewcommand\thefigure{%s}'%\
                                 references[key]])
                pre = RawBlock('tex', tex)
                tex = '\n'.join([r'\let\thefigure=\oldthefigure',
                                 r'\addtocounter{figure}{-1}'])
                post = RawBlock('tex', tex)
                return [pre, Para(value), post]
        elif fig['is_unreferenceable']:
            attrs[0] = ''  # The label isn't needed any further
        elif PANDOCVERSION < '1.16' and fmt in ('html', 'html5') \
          and LABEL_PATTERN.match(attrs[0]):
            # Insert anchor
            anchor = RawBlock('html', '<a name="%s"></a>'%attrs[0])
            return [anchor, Para(value)]
        elif fmt == 'docx':
            # As per http://officeopenxml.com/WPhyperlink.php
            bookmarkstart = \
              RawBlock('openxml',
                       '<w:bookmarkStart w:id="0" w:name="%s"/>'
                       %attrs[0])
            bookmarkend = \
              RawBlock('openxml', '<w:bookmarkEnd w:id="0"/>')
            return [bookmarkstart, Para(value), bookmarkend]

    return None


# Main program ---------------------------------------------------------------

# Define \@makenoprefixcaption to make a caption without a prefix.  This
# should replace \@makecaption as needed.  See the standard \@makecaption TeX
# at https://stackoverflow.com/questions/2039690.  The macro gets installed
# using an environment.  The \thefigure counter must be set to something unique
# so that duplicate names are avoided.  This must be done the hyperref
# counter \theHfigure as well; see Sect. 3.9 of
# http://ctan.mirror.rafal.ca/macros/latex/contrib/hyperref/doc/manual.html.

TEX0 = r"""
% pandoc-xnos: macro to create a caption without a prefix
\makeatletter
\long\def\@makenoprefixcaption#1#2{
  \vskip\abovecaptionskip
  \sbox\@tempboxa{#2}
  \ifdim \wd\@tempboxa >\hsize
    #2\par
  \else
    \global \@minipagefalse
    \hb@xt@\hsize{\hfil\box\@tempboxa\hfil}
  \fi
  \vskip\belowcaptionskip}
\makeatother
""".strip()

TEX1 = r"""
% pandoc-fignos: save original macros
\makeatletter
\let\@oldmakecaption=\@makecaption
\let\oldthefigure=\thefigure
\let\oldtheHfigure=\theHfigure
\makeatother
""".strip()

TEX2 = r"""
% pandoc-fignos: environment disables figure caption prefixes
\makeatletter
\newcounter{figno}
\newenvironment{no-prefix-figure-caption}{
  \let\@makecaption=\@makenoprefixcaption
  \renewcommand\thefigure{x.\thefigno}
  \renewcommand\theHfigure{x.\thefigno}
  \stepcounter{figno}
}{
  \let\thefigure=\oldthefigure
  \let\theHfigure=\oldtheHfigure
  \let\@makecaption=\@oldmakecaption
  \addtocounter{figure}{-1}
}
\makeatother
""".strip()

# TeX to set the caption name
TEX3 = r"""
%% pandoc-fignos: caption name
\renewcommand{\figurename}{%s}
""".strip()


def process(meta):
    """Saves metadata fields in global variables and returns a few
    computed fields."""

    # pylint: disable=global-statement
    global capitalize
    global captionname
    global use_cleveref_default
    global plusname
    global starname
    global numbersections

    # Read in the metadata fields and do some checking

    for name in ['fignos-caption-name', 'figure-name']:
        # 'figure-name' is deprecated
        if name in meta:
            captionname = get_meta(meta, name)
            assert isinstance(captionname, STRTYPES)
            break

    for name in ['fignos-cleveref', 'xnos-cleveref', 'cleveref']:
        # 'xnos-cleveref' enables cleveref in all 3 of fignos/eqnos/tablenos
        # 'cleveref' is deprecated
        if name in meta:
            use_cleveref_default = check_bool(get_meta(meta, name))
            break

    for name in ['fignos-capitalize', 'fignos-capitalise',
                 'xnos-capitalize', 'xnos-capitalise']:
        # 'fignos-capitalise' is an alternative spelling
        # 'xnos-capitalise' enables capitalise in all 3 of fignos/eqnos/tablenos
        # 'xnos-capitalize' is an alternative spelling
        if name in meta:
            capitalize = check_bool(get_meta(meta, name))
            break

    if 'fignos-plus-name' in meta:
        tmp = get_meta(meta, 'fignos-plus-name')
        if isinstance(tmp, list):
            plusname = tmp
        else:
            plusname[0] = tmp
        assert len(plusname) == 2
        for name in plusname:
            assert isinstance(name, STRTYPES)

    if 'fignos-star-name' in meta:
        tmp = get_meta(meta, 'fignos-star-name')
        if isinstance(tmp, list):
            starname = tmp
        else:
            starname[0] = tmp
        assert len(starname) == 2
        for name in starname:
            assert isinstance(name, STRTYPES)

    if 'xnos-number-sections' in meta:
        numbersections = check_bool(get_meta(meta, 'xnos-number-sections'))


def main():
    """Filters the document AST."""

    # pylint: disable=global-statement
    global PANDOCVERSION
    global Image

    # Get the output format and document
    fmt = args.fmt
    doc = json.loads(STDIN.read())

    # Initialize pandocxnos
    # pylint: disable=too-many-function-args
    PANDOCVERSION = pandocxnos.init(args.pandocversion, doc)

    # Element primitives
    if PANDOCVERSION < '1.16':
        Image = elt('Image', 2)

    # Chop up the doc
    meta = doc['meta'] if PANDOCVERSION >= '1.18' else doc[0]['unMeta']
    blocks = doc['blocks'] if PANDOCVERSION >= '1.18' else doc[1:]

    # Process the metadata variables
    process(meta)

    # First pass
    attach_attrs_image = attach_attrs_factory(Image,
                                              extract_attrs=_extract_attrs)
    detach_attrs_image = detach_attrs_factory(Image)
    insert_secnos = insert_secnos_factory(Image)
    delete_secnos = delete_secnos_factory(Image)
    filters = [insert_secnos, process_figures, delete_secnos] \
      if PANDOCVERSION >= '1.16' else \
      [attach_attrs_image, insert_secnos, process_figures,
       delete_secnos, detach_attrs_image]
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               filters, blocks)

    # Second pass
    process_refs = process_refs_factory(references.keys())
    replace_refs = replace_refs_factory(references,
                                        use_cleveref_default, False,
                                        plusname if not capitalize else
                                        [name.title() for name in plusname],
                                        starname, 'figure')
    attach_attrs_span = attach_attrs_factory(Span, replace=True)
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [repair_refs, process_refs, replace_refs,
                                attach_attrs_span],
                               altered)

    # Insert supporting TeX
    if fmt == 'latex':

        rawblocks = []

        if has_unnumbered_figures:
            rawblocks += [RawBlock('tex', TEX0),
                          RawBlock('tex', TEX1),
                          RawBlock('tex', TEX2)]

        if captionname != 'Figure':
            rawblocks += [RawBlock('tex', TEX3 % captionname)]

        insert_rawblocks = insert_rawblocks_factory(rawblocks)

        altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                                   [insert_rawblocks], altered)

    # Update the doc
    if PANDOCVERSION >= '1.18':
        doc['blocks'] = altered
    else:
        doc = doc[:1] + altered

    # Dump the results
    json.dump(doc, STDOUT)

    # Flush stdout
    STDOUT.flush()

if __name__ == '__main__':
    main()
