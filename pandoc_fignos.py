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

from pandocfilters import walk
from pandocfilters import RawBlock, RawInline
from pandocfilters import Str, Para, Plain, elt

import pandocfiltering
from pandocfiltering import get_meta, STRTYPES
from pandocfiltering import repair_refs, use_refs_factory
from pandocfiltering import pandocify
from pandocfiltering import use_attrimages, filter_attrimages
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
AttrImage = elt('Image', 3)  # Pandoc >= 1.16

# Pattern for matching labels
LABEL_PATTERN = re.compile(r'(fig:[\w/-]*)')

references = {}  # Global references tracker

# Meta variables; may be reset elsewhere
captionname = 'Figure'            # Used with \figurename
plusname = ['fig.', 'figs.']      # Used with \cref
starname = ['Figure', 'Figures']  # Used with \Cref
cleveref_default = False          # Default setting for clever referencing

# Flags that cleveref tex is needed
clevereftex = False


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

def replace_figures(key, value, fmt, meta): # pylint: disable=unused-argument
    """Replaces figures while storing reference labels."""

    if key == 'Para':

        # Prepend html anchors for figures.
        if fmt in ('html', 'html5') and is_figure(key, value):
            attrs, caption, target = parse_figure(key, value)
            if LABEL_PATTERN.match(attrs[0]):
                anchor = RawInline('html', '<a name="%s"></a>'%attrs[0])
                return [Plain([anchor]), Para(value)]

    elif is_figure(key, value):

        # Parse the image
        attrs, caption, target = parse_figure(key, value)

        # Bail out if the label does not conform
        if not attrs[0] or not LABEL_PATTERN.match(attrs[0]):
            # Attributed images are not supported by pandoc < 1.16
            return Image(caption, target) if PANDOCVERSION < '1.16' else None

        # Save the reference
        references[attrs[0]] = len(references) + 1

        # Adjust caption depending on the output format
        if fmt == 'latex':
            caption = list(caption) + [RawInline('tex', r'\label{%s}'%attrs[0])]
        else:
            caption = pandocify('%s %d. '%(captionname, references[attrs[0]])) \
              + list(caption)

        # Return the replacement
        if PANDOCVERSION >= '1.17' and fmt == 'latex':
            # Remove id from the image attributes.  It is incorrectly
            # handled by pandoc's TeX writer for these versions
            if LABEL_PATTERN.match(attrs[0]):
                attrs[0] = ''
        return AttrImage(attrs, caption, target)


def replace_refs(key, value, fmt, meta):  # pylint: disable=unused-argument
    """Replaces references to labelled images."""

    global clevereftex  # pylint: disable=global-statement

    if key == 'Ref':

        # Parse the figure reference
        attrs, label = value
        attrs = PandocAttributes(attrs, 'pandoc')

        # Check if we need cleveref tex
        if not clevereftex:
            if 'modifier' in attrs.kvs and attrs['modifier'] in ['*', '+']:
                clevereftex = True

        # Choose between \Cref, \cref and \ref
        cleveref = attrs['modifier'] in ['*', '+'] \
          if 'modifier' in attrs.kvs else cleveref_default
        plus = attrs['modifier'] == '+' if 'modifier' in attrs.kvs \
          else cleveref_default

        # The replacement depends on the output format
        if fmt == 'latex':
            if cleveref:
                macro = r'\cref' if plus else r'\Cref'
                return RawInline('tex', r'%s{%s}'%(macro, label))
            else:
                return RawInline('tex', r'\ref{%s}'%label)
        elif fmt in ('html', 'html5'):
            if cleveref:
                name = plusname[0] if plus else starname[0]
                link = '%s <a href="#%s">%s</a>' % \
                  (name, label, references[label])
            else:
                link = '<a href="#%s">%s</a>' % (label, references[label])
            return RawInline('html', link)
        else:
            name = plusname[0] if plus else starname[0]
            if cleveref:
                return Str('%s %d'%(name, references[label]))
            else:
                return Str('%d'%references[label])


# Main program ---------------------------------------------------------------

def process(meta):
    """Saves metadata fields in global variables and returns a few
    computed fields."""

    # pylint: disable=global-statement
    global captionname, cleveref_default, clevereftex, plusname, starname

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
        clevereftex = cleveref_default = get_meta(meta, 'cleveref')
        assert cleveref_default in [True, False]

    if 'fignos-cleveref' in meta:
        clevereftex = cleveref_default = get_meta(meta, 'fignos-cleveref')
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
                               [repair_refs, use_attrimages, replace_figures,
                                filter_attrimages], doc)

    # Second pass
    use_refs = use_refs_factory(references.keys())
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [use_refs, replace_refs], altered)

    # For latex/pdf, inject command to change caption name
    if fmt == 'latex' and captionname != 'Figure':
        tex = r'\renewcommand{\figurename}{%s}'%captionname
        altered[1] = [RawBlock('tex', tex)] + altered[1]

    # For latex/pdf, inject a command to fake \cref when it is missing
    if clevereftex and fmt == 'latex':
        tex1 = r'\providecommand{\cref}{%s~\ref}' % plusname[0]
        tex2 = r'\providecommand{\Cref}{%s~\ref}' % starname[0]
        altered[1] = [RawBlock('tex', tex1), RawBlock('tex', tex2)] + altered[1]

    # For latex/pdf, inject commands if plusname and/or starname are changed
    if plusnametex:
        altered[1] = [RawBlock('tex', plusnametex)] + altered[1]
    if starnametex:
        altered[1] = [RawBlock('tex', starnametex)] + altered[1]

    # Dump the results
    json.dump(altered, STDOUT)

    # Flush stdout
    STDOUT.flush()

if __name__ == '__main__':
    main()
