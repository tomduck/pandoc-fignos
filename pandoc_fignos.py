#! /usr/bin/env python

"""pandoc-fignos: a pandoc filter that inserts figure nos. and refs."""

# Copyright 2015, 2016 Thomas J. Duck.
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
# The basic idea is to scan the AST two times in order to:
#
#   1. Insert text for the figure number in each figure caption.
#      For LaTeX, insert \label{...} instead.  The figure ids
#      and associated figure numbers are stored in the global
#      references tracker.
#
#   2. Replace each reference with a figure number.  For LaTeX,
#      replace with \ref{...} instead.

# pylint: disable=invalid-name

import re
import functools
import argparse
import json

import sys
if sys.version_info > (3,):
    from urllib.request import unquote  # pylint: disable=no-name-in-module
else:
    from urllib import unquote  # pylint: disable=no-name-in-module

from pandocfilters import walk
from pandocfilters import RawBlock, RawInline
from pandocfilters import Str, Para, Plain, elt

import pandocfiltering
from pandocfiltering import STRTYPES
from pandocfiltering import get_meta, extract_attrs
from pandocfiltering import repair_refs, use_refs_factory, replace_refs_factory
from pandocfiltering import use_attrs_factory, filter_attrs_factory
from pandocfiltering import pandocify
from pandocfiltering import STDIN, STDOUT

from pandocattributes import PandocAttributes

# Read the command-line arguments
parser = argparse.ArgumentParser(description='Pandoc figure numbers filter.')
parser.add_argument('fmt')
parser.add_argument('--pandocversion', help='The pandoc version.')
args = parser.parse_args()

# Set/get PANDOCVERSION
pandocfiltering.init(args.pandocversion)
PANDOCVERSION = pandocfiltering.PANDOCVERSION

# Create our own pandoc image primitives
Image = elt('Image', 2)      # Pandoc < 1.16

# Pattern for matching labels
LABEL_PATTERN = re.compile(r'(fig:[\w/-]*)')

references = {}  # Global references tracker

# Meta variables; may be reset elsewhere
captionname = 'Figure'            # Used with \figurename
plusname = ['fig.', 'figs.']      # Used with \cref
starname = ['Figure', 'Figures']  # Used with \Cref
cleveref_default = False          # Default setting for clever referencing


# Helper functions ----------------------------------------------------------

def is_figure(key, value):
    """True if this is a figure; False otherwise."""
    if key == 'Para' and len(value) == 1:
        return is_figure(value[0]['t'], value[0]['c'])  # Recursive call
    elif key == 'Image' and len(value) == 3:
        # pylint: disable=unused-variable
        attrs, caption, target = value
        return target[1] == 'fig:'  # Pandoc uses this as a figure marker
    else:
        return False

def parse_figure(key, value):
    """Parses the value from a figure."""
    if key == 'Para':
        assert is_figure(key, value)
        return parse_figure(value[0]['t'], value[0]['c'])
    else:
        assert key == 'Image'
        attrs, caption, target = value
        if attrs[0] == 'fig:': # Make up a unique description
            attrs[0] = 'fig:' + '__'+str(hash(target[0]))+'__'
        return attrs, caption, target


# Actions --------------------------------------------------------------------

def _extract_imageattrs(value, n):
    """Extracts attributes from a list of values.  n is the index where the
    attributes begin.  Extracted elements are deleted from the value list.
    Attrs are returned in pandoc format.
    """

    try:
        return extract_attrs(value, n)

    except (ValueError, IndexError):
        # Look for attributes attached to the image path, as occurs with
        # reference links.  Remove the encoding.
        assert value[n-1]['t'] == 'Image'
        image = value[n-1]

        try:
            seq = unquote(image['c'][1][0]).split()
            path, s = seq[0], ' '.join(seq[1:])
        except ValueError:
            pass
        else:
            image['c'][1][0] = path  # Remove attr string from the path
            return PandocAttributes(s.strip(), 'markdown').to_pandoc()

def use_attrs_images(key, value, fmt, meta):
    """Attaches attributes to Image elements (pandoc < 1.16)."""
    if PANDOCVERSION < '1.16':
        action = use_attrs_factory('Image', extract_attrs=_extract_imageattrs)
        return action(key, value, fmt, meta)
    else:
        return # Images are already attributed for pandoc >= 1.16

def filter_attrs_images(key, value, fmt, meta):
    """Filters attributes from Image elements (pandoc < 1.16)."""
    if PANDOCVERSION < '1.16':
        action = filter_attrs_factory('Image', 2)
        return action(key, value, fmt, meta)
    else:
        return # Images are already attributed for pandoc >= 1.16

def process_figures(key, value, fmt, meta): # pylint: disable=unused-argument
    """Processes the figures."""

    if key == 'Para':

        # Prepend html anchors for figures.
        if fmt in ('html', 'html5') and is_figure(key, value):
            # pylint: disable=unused-variable
            attrs, caption, target = parse_figure(key, value)
            if LABEL_PATTERN.match(attrs[0]):
                anchor = RawInline('html', '<a name="%s"></a>'%attrs[0])
                return [Plain([anchor]), Para(value)]

    elif is_figure(key, value):

        # Parse the image
        attrs, caption, target = parse_figure(key, value)

        # Bail out if the label does not conform
        if not attrs[0] or not LABEL_PATTERN.match(attrs[0]):
            return

        # Save the reference
        references[attrs[0]] = len(references) + 1

        # Adjust caption depending on the output format
        value[1] = list(caption) + [RawInline('tex', r'\label{%s}'%attrs[0])] \
          if fmt == 'latex' else \
          pandocify('%s %d. '%(captionname, references[attrs[0]])) \
          + list(caption)
              
        if PANDOCVERSION >= '1.17' and fmt == 'latex':
            # Remove id from the image attributes.  It is incorrectly
            # handled by pandoc's TeX writer for these versions
            if LABEL_PATTERN.match(attrs[0]):
                attrs[0] = ''


# Main program ---------------------------------------------------------------

def process(meta):
    """Saves metadata fields in global variables and returns a few
    computed fields."""

    # pylint: disable=global-statement
    global captionname, cleveref_default, plusname, starname

    # Initialize computed fields
    plusnametex = None
    starnametex = None

    # Read in the metadata fields and do some checking

    if 'fignos-caption-name' in meta:
        captionname = get_meta(meta, 'fignos-caption-name')
        assert type(captionname) in STRTYPES
    elif 'figure-name' in meta:  # Deprecated
        captionname = get_meta(meta, 'figure-name')
        assert type(captionname) in STRTYPES

    if 'cleveref' in meta:
        cleveref_default = get_meta(meta, 'cleveref')
        assert cleveref_default in [True, False]

    if 'fignos-cleveref' in meta:
        cleveref_default = get_meta(meta, 'fignos-cleveref')
        assert cleveref_default in [True, False]

    if 'fignos-plus-name' in meta:
        tmp = get_meta(meta, 'fignos-plus-name')
        if type(tmp) is list:
            plusname = tmp
        else:
            plusname[0] = tmp
        assert len(plusname) == 2
        for name in plusname:
            assert type(name) in STRTYPES

        # LaTeX to inject
        plusnametex = \
            r'\providecommand{\crefname}[3]{}\crefname{figure}{%s}{%s}'%\
            (plusname[0], plusname[1])

    if 'fignos-star-name' in meta:
        tmp = get_meta(meta, 'fignos-star-name')
        if type(tmp) is list:
            starname = tmp
        else:
            starname[0] = tmp
        assert len(starname) == 2
        for name in starname:
            assert type(name) in STRTYPES

        # LaTeX to inject
        starnametex = \
            r'\providecommand{\Crefname}[3]{}\Crefname{figure}{%s}{%s}'%\
            (starname[0], starname[1])

    return plusnametex, starnametex


def main():
    """Filters the document AST."""

    # Get the output format, document and metadata
    fmt = args.fmt
    doc = json.loads(STDIN.read())
    meta = doc[0]['unMeta']

    # Process the metadata variables
    plusnametex, starnametex = process(meta)

    # First pass
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [repair_refs, use_attrs_images, process_figures,
                                filter_attrs_images], doc)

    # Second pass
    use_refs = use_refs_factory(references.keys())
    replace_refs = replace_refs_factory(references, cleveref_default,
                                    plusname, starname)
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [use_refs, replace_refs], altered)


    # Assemble supporting TeX
    if fmt == 'latex':
        tex = []

        # Change caption name
        if captionname != 'Figure':
            tex.append(r'\renewcommand{\figurename}{%s}'%captionname)

        # Fake \cref and \Cref when they are missing
        tex += pandocfiltering.clevereftex

        # Include plusnametex and starnametex
        if plusnametex:
            tex.append(plusnametex)
        if starnametex:
            tex.append(starnametex)

        altered[1] = [RawBlock('tex', '\n'.join(tex))] + altered[1]


    # Dump the results
    json.dump(altered, STDOUT)

    # Flush stdout
    STDOUT.flush()

if __name__ == '__main__':
    main()
