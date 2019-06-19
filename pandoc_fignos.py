#! /usr/bin/env python

"""pandoc-fignos: a pandoc filter that inserts figure nos. and refs."""


__version__ = '2.0.0a1'


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
#
# This is followed by injecting header code as needed for certain output
# formats.


# pylint: disable=invalid-name

import sys
import re
import functools
import argparse
import json
import uuid
import copy
import textwrap

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

if sys.version_info > (3,):
    from urllib.request import unquote  # pylint: disable=no-name-in-module
else:
    from urllib import unquote  # pylint: disable=no-name-in-module


# Read the command-line arguments
parser = argparse.ArgumentParser(description='Pandoc figure numbers filter.')
parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))
parser.add_argument('fmt')
parser.add_argument('--pandocversion', help='The pandoc version.')
args = parser.parse_args()

# Pattern for matching labels
LABEL_PATTERN = re.compile(r'(fig:[\w/-]*)')

# Meta variables; may be reset elsewhere
captionname = 'Figure'  # The caption name
cleveref = False        # Flags that clever references should be used
capitalise = False      # Flags that plusname should be capitalised
plusname = ['fig.', 'figs.']      # Sets names for mid-sentence references
starname = ['Figure', 'Figures']  # Sets names for references at sentence start
numbersections = False  # Flags that sections should be numbered by section

# Processing state variables
cursec = None          # Current section
Nreferences = 0        # Number of references in current section (or document)
references = {}        # Tracks referenceable figures and their numbers/tags
unreferenceable = []   # List of figures that are unreferenceable

# Processing flags
captionname_changed = False     # Flags the the caption name changed
plusname_changed = False        # Flags that the plus name changed
starname_changed = False        # Flags that the star name changed
has_unnumbered_figures = False  # Flags unnumbered figures were found
has_tagged_figures = False      # Flags a tagged figure was found
replaced_figure_env = False     # Flags that the figure environment is replaced

PANDOCVERSION = None


# Actions --------------------------------------------------------------------

def _extract_attrs(x, n):
    """Extracts attributes for an image.  n is the index where the
    attributes begin in the element list x.  Extracted elements are deleted
    from the list.  Attrs are returned in pandoc format.
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


def _adjust_caption(fmt, fig, attrs, value, caption):
    """Adjust the caption depending on the output format."""
    if fmt in ['latex', 'beamer']:  # Append a \label if this is referenceable
        if not fig['is_unreferenceable']:
            value[0]['c'][1] += \
              [RawInline('tex', r'\protect\label{%s}'%attrs[0])]
    else:  # Hard-code in the caption name and number/tag
        if isinstance(references[attrs[0]], int):  # Numbered reference
            if fmt in ['html', 'html5', 'epub', 'epub2', 'epub3']:
                value[0]['c'][1] = [RawInline('html', r'<span>'),
                                    Str(captionname), Space(),
                                    Str('%d:'%references[attrs[0]]),
                                    RawInline('html', r'</span>')]
            else:
                value[0]['c'][1] = [Str(captionname),
                                    Space(),
                                    Str('%d:'%references[attrs[0]])]
            value[0]['c'][1] += [Space()] + list(caption)
        else:  # Tagged reference
            assert isinstance(references[attrs[0]], STRTYPES)
            text = references[attrs[0]]
            if text.startswith('$') and text.endswith('$'):  # Math
                math = text.replace(' ', r'\ ')[1:-1]
                els = [Math({"t":"InlineMath", "c":[]}, math), Str(':')]
            else:  # Text
                els = [Str(text+':')]
                if fmt in ['html', 'html5', 'epub', 'epub2', 'epub3']:
                    value[0]['c'][1] = \
                      [RawInline('html', r'<span>'),
                       Str(captionname),
                       Space()] + els + [RawInline('html', r'</span>')]
                else:
                    value[0]['c'][1] = [Str(captionname), Space()] + els
            value[0]['c'][1] += [Space()] + list(caption)


def _process_figure(value, fmt):
    """Processes a figure.  Returns a dict containing figure properties."""

    # pylint: disable=global-statement
    global cursec        # Current section being processed
    global Nreferences   # Number of refs in current section (or document)
    global has_unnumbered_figures  # Flags that unnumbered figures were found

    # Parse the image
    attrs, caption = value[0]['c'][:2]

    # Initialize the return value
    fig = {'is_unnumbered': False,
           'is_unreferenceable': False,
           'is_tagged': False,
           'env': None,
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

    # Get the kvs
    kvs = PandocAttributes(attrs, 'pandoc').kvs

    # Store the environment
    if 'env' in kvs:
        fig['env'] = kvs['env']

    # Pandoc's --number-sections supports section numbering latex/pdf, html,
    # epub, and docx
    if numbersections:
        # Latex/pdf supports equation numbers by section natively.  For the
        # other formats we must hard-code in equation numbers by section as
        # tags.
        if fmt in ['html', 'html5', 'epub', 'epub2', 'epub3', 'docx'] and \
          'tag' not in kvs:
            if kvs['secno'] != cursec:  # The section number changed
                cursec = kvs['secno']   # Update the global section tracker
                Nreferences = 1         # Resets the global reference counter
            kvs['tag'] = cursec + '.' + str(Nreferences)
            Nreferences += 1

    # Save to the global references tracker
    fig['is_tagged'] = 'tag' in kvs
    if fig['is_tagged']:  # ... then save the tag
        # Remove any surrounding quotes
        if kvs['tag'][0] == '"' and kvs['tag'][-1] == '"':
            kvs['tag'] = kvs['tag'].strip('"')
        elif kvs['tag'][0] == "'" and kvs['tag'][-1] == "'":
            kvs['tag'] = kvs['tag'].strip("'")
        references[attrs[0]] = kvs['tag']
    else:  # ... then save the figure number
        Nreferences += 1  # Increment the global reference counter
        references[attrs[0]] = Nreferences

    # Adjust the caption depending on the output format
    _adjust_caption(fmt, fig, attrs, value, caption)

    return fig


def _context_dependent_output(fmt, fig, value, unnumbered_figure_ret_tex):
    """Assembles and returns context-dependent output."""

    # pylint: disable=global-statement
    global has_tagged_figures       # Flags a tagged figure was found
    global replaced_figure_env      # Flags that the figure env is replaced

    # Context-dependent output
    ret = None
    attrs = fig['attrs']
    if fig['is_unnumbered']:
        # Unnumbered is also unreferenceable
        if fmt in ['latex', 'beamer']:
            if fig['env']:
                # Replace the figure environment
                replaced_figure_env = True
                ret = [RawBlock('tex', r'\begin{fignos:figure-env}[%s]' % \
                                fig['env']),
                       Para(value),
                       RawBlock('tex', r'\end{fignos:figure-env}')]
            ret = unnumbered_figure_ret_tex
    elif fmt in ['latex', 'beamer']:
        key = attrs[0]
        if PANDOCVERSION >= '1.17':  # Is this still needed???
            # Remove id from the image attributes.  It is incorrectly
            # handled by pandoc's TeX writer for these versions.
            if LABEL_PATTERN.match(attrs[0]):
                attrs[0] = ''
        if fig['is_tagged']:
            # Switch to the tagged-figure env
            has_tagged_figures = True
            ret = [RawBlock('tex', r'\begin{fignos:tagged-figure}[%s]' % \
                            references[key]),
                   Para(value),
                   RawBlock('tex', r'\end{fignos:tagged-figure}')]
        if fig['env']:
            # Replace the figure environment.  Note that tagging figures
            # and switching environments are mutually exclusive.
            replaced_figure_env = True
            ret = [RawBlock('tex', r'\begin{fignos:figure-env}[%s]' % \
                            fig['env']),
                   Para(value),
                   RawBlock('tex', r'\end{fignos:figure-env}')]
    elif fig['is_unreferenceable']:
        attrs[0] = ''  # The label isn't needed any further
    elif PANDOCVERSION < '1.16' \
      and fmt in ('html', 'html5', 'epub', 'epub2', 'epub3') \
      and LABEL_PATTERN.match(attrs[0]):
        # Insert anchor for PANDOCVERSION < 1.16; for later versions
        # the id is installed by pandoc.
        anchor = RawBlock('html', '<a name="%s"></a>'%attrs[0])
        ret = [anchor, Para(value)]
    elif fmt == 'docx':
        # As per http://officeopenxml.com/WPhyperlink.php
        bookmarkstart = \
          RawBlock('openxml',
                   '<w:bookmarkStart w:id="0" w:name="%s"/>'
                   %attrs[0])
        bookmarkend = \
          RawBlock('openxml', '<w:bookmarkEnd w:id="0"/>')
        ret = [bookmarkstart, Para(value), bookmarkend]

    return ret


def process_figures(key, value, fmt, meta): # pylint: disable=unused-argument
    """Processes the figures."""

    # pylint: disable=global-statement
    global has_unnumbered_figures   # Flags that unnumbered figures were found

    # Process figures wrapped in Para elements
    if key == 'Para' and len(value) == 1 and \
      value[0]['t'] == 'Image' and value[0]['c'][-1][1].startswith('fig:'):

        # Return element list for unnumbered figures for latex/pdf.  Disables
        # the figure caption prefix (i.e., "Fig. 1:").
        unnumbered_figure_ret_tex = \
          [RawBlock('tex', r'\begin{fignos:no-prefix-figure-caption}'),
           Para(value),
           RawBlock('tex', r'\end{fignos:no-prefix-figure-caption}')]

        # Inspect the image
        if len(value[0]['c']) == 2:  # Unattributed figure, bail out
            # Unnumbered is also unreferenceable
            has_unnumbered_figures = True
            if fmt in ['latex', 'beamer']:
                return unnumbered_figure_ret_tex
            return None

        # Process the figure and return context-dependent output
        fig = _process_figure(value, fmt)
        return _context_dependent_output(fmt, fig, value,
                                         unnumbered_figure_ret_tex)

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
    \renewcommand{\thefigure}{yyz\thefigno}
    \renewcommand{\theHfigure}{yyz\thefigno}
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

# Define an environment to replace the figure environment
FIGURE_ENV_TEX = r"""
%% pandoc-fignos: environment to replace the figure environment
\makeatletter
\newenvironment{fignos:figure-env}[1][]{
  \def\@temp{#1}
  \expandafter\ifx\csname #1\endcsname\relax
  \else
    \let\oldfigure\figure
    \let\oldendfigure\endfigure
    \renewenvironment{figure}{\begin{#1}}{\end{#1}}
  \fi
}{
  \expandafter\ifx\csname \@temp\endcsname\relax
  \else
    \let\figure\oldfigure
    \let\endfigure\oldendfigure
  \fi
}
\makeatother
"""

# Reset the caption name; i.e. change "Figure" at the beginning of a caption
# to something else.
CAPTION_NAME_TEX = r"""
%% pandoc-fignos: change the caption name
\renewcommand{\figurename}{%s}
"""


# Main program ---------------------------------------------------------------

# pylint: disable=too-many-branches
def process(meta):
    """Saves metadata fields in global variables and returns a few
    computed fields."""

    # pylint: disable=global-statement
    global captionname     # The caption name
    global cleveref        # Flags that clever references should be used
    global capitalise      # Flags that plusname should be capitalised
    global plusname        # Sets names for mid-sentence references
    global starname        # Sets names for references at sentence start
    global numbersections  # Flags that sections should be numbered by section
    global captionname_changed  # Flags the the caption name changed
    global plusname_changed     # Flags that the plus name changed
    global starname_changed     # Flags that the star name changed

    # Read in the metadata fields and do some checking

    if 'fignos-caption-name' in meta:
        old_captionname = captionname
        captionname = get_meta(meta, 'fignos-caption-name')
        captionname_changed = captionname != old_captionname
        assert isinstance(captionname, STRTYPES)

    for name in ['fignos-cleveref', 'xnos-cleveref']:
        # 'xnos-cleveref' enables cleveref in all 3 of fignos/eqnos/tablenos
        if name in meta:
            cleveref = check_bool(get_meta(meta, name))
            break

    for name in ['fignos-capitalize', 'fignos-capitalise',
                 'xnos-capitalize', 'xnos-capitalise']:
        # 'fignos-capitalise' is an alternative spelling
        # 'xnos-capitalise' enables capitalise in all 3 of fignos/eqnos/tablenos
        # 'xnos-capitalize' is an alternative spelling
        if name in meta:
            capitalise = check_bool(get_meta(meta, name))
            break

    if 'fignos-plus-name' in meta:
        tmp = get_meta(meta, 'fignos-plus-name')
        old_plusname = copy.deepcopy(plusname)
        if isinstance(tmp, list):
            # The singular and plural forms were given in a list
            plusname = tmp
        else:
            # Only the singular form was given
            plusname[0] = tmp
        plusname_changed = plusname != old_plusname
        assert len(plusname) == 2
        for name in plusname:
            assert isinstance(name, STRTYPES)

    if 'fignos-star-name' in meta:
        tmp = get_meta(meta, 'fignos-star-name')
        old_starname = copy.deepcopy(starname)
        if isinstance(tmp, list):
            # Only the singular form was given
            starname = tmp
        else:
            # The singular and plural forms were given in a list
            starname[0] = tmp
        starname_changed = starname != old_starname
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
                                        cleveref, False,
                                        plusname if not capitalise \
                                        or plusname_changed else
                                        [name.title() for name in plusname],
                                        starname, 'figure')
    attach_attrs_span = attach_attrs_factory(Span, replace=True)
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [repair_refs, process_refs, replace_refs,
                                attach_attrs_span],
                               altered)

    if fmt in ['latex', 'beamer']:

        # Update the header-includes metadata.  Pandoc's
        # --include-in-header option will override anything we do here.  This
        # is a known issue and is owing to a design decision in pandoc.
        # See https://github.com/jgm/pandoc/issues/3139.

        if pandocxnos.cleveref_required():
            pandocxnos.add_package_to_header_includes(
                'fignos', meta, 'cleveref',
                'capitalise' if capitalise else None)

        if has_unnumbered_figures:
            pandocxnos.add_package_to_header_includes(meta, 'caption')

        if plusname_changed:
            tex = textwrap.dedent("""
                %%%% pandoc-fignos: change cref names
                \\crefname{figure}{%s}{%s}
            """ % (plusname[0], plusname[1]))
            pandocxnos.add_tex_to_header_includes(meta, tex)

        if starname_changed:
            tex = textwrap.dedent("""
                %%%% pandoc-fignos: change Cref names
                \\Crefname{figure}{%s}{%s}
            """ % (starname[0], starname[1]))
            pandocxnos.add_tex_to_header_includes(meta, tex)

        if has_unnumbered_figures:
            pandocxnos.add_tex_to_header_includes(
                meta, NO_PREFIX_CAPTION_ENV_TEX)

        if has_tagged_figures:
            pandocxnos.add_tex_to_header_includes(
                meta, TAGGED_FIGURE_ENV_TEX)

        if replaced_figure_env:
            pandocxnos.add_tex_to_header_includes(meta, FIGURE_ENV_TEX)

        if captionname != 'Figure':
            pandocxnos.add_tex_to_header_includes(
                meta, CAPTION_NAME_TEX % captionname)

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
