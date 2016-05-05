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
from pandocfiltering import repair_refs, pandocify
from pandocfiltering import use_attrimages, filter_attrimages
from pandocfiltering import use_refs_factory
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

# Patterns for matching labels and references
LABEL_PATTERN = re.compile(r'(fig:[\w/-]*)')
REF_PATTERN = re.compile(r'@(fig:[\w/-]+)')

references = {}  # Global references tracker

# Meta variables; may be reset elsewhere
figurename = 'Figure'
figurelong = 'Figure'
figureabbrev = 'fig.'
default_cref = False

# Flags that cleveref must be included in TeX documents
include_cref = False


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
            caption = pandocify('%s %d. '%(figurename, references[attrs[0]])) \
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

    global include_cref  # pylint: disable=global-statement

    if key == 'Ref':

        # Parse the figure reference
        attrs, label = value
        attrs = PandocAttributes(attrs, 'pandoc')

        # Check for cref usage
        if not include_cref:
            if 'modifier' in attrs.kvs and attrs['modifier'] in ['*', '+']:
                include_cref = True

        # Choose between \Cref, \cref and \ref
        cref = attrs['modifier'] in ['*', '+'] if 'modifier' in attrs.kvs \
          else default_cref
        use_abbrev = attrs['modifier'] == '+' if 'modifier' in attrs.kvs \
          else False

        # The replacement depends on the output format
        if fmt == 'latex':
            if cref:
                macro = r'\cref' if use_abbrev else r'\Cref'
                return RawInline('tex', r'%s{%s}'%(macro, label))
            else:
                return RawInline('tex', r'\ref{%s}'%label)
        elif fmt in ('html', 'html5'):
            if cref:
                name = figureabbrev if use_abbrev else figurelong
                link = '%s <a href="#%s">%s</a>' % \
                  (name, label, references[label])
            else:
                link = '<a href="#%s">%s</a>' % (label, references[label])
            return RawInline('html', link)
        else:
            name = figureabbrev if use_abbrev else figurelong
            if cref:
                return Str('%s %d'%(name, references[label]))
            else:
                return Str('%d'%references[label])


# Main program ---------------------------------------------------------------

def main():
    """Filters the document AST."""

    # pylint: disable=global-statement
    global figurename, figurelong, figureabbrev, default_cref, include_cref

    # Get the output format, document and metadata
    fmt = args.fmt
    doc = json.loads(STDIN.read())
    meta = doc[0]['unMeta']

    # Extract meta variables
    def _get_meta(name):
        ret = meta[name]['c']  # Works for cmdline vars
        if type(ret) is list:  # For YAML vars
            ret = ret[0]['c']
        return ret
    if 'figure-name' in meta:
        figurename = _get_meta('figure-name')
    if 'figure-long' in meta:
        figurelong = _get_meta('figure-long')
    if 'figure-abbrev' in meta:
        figureabbrev = _get_meta('figure-abbrev')
    if 'cref' in meta:
        include_cref = default_cref = _get_meta('cref')
    if 'fignos-cref' in meta:
        include_cref = default_cref = _get_meta('fignos-cref')

    # First pass
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [repair_refs, use_attrimages, replace_figures,
                                filter_attrimages], doc)

    # Second pass
    use_refs = use_refs_factory(references.keys())
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [use_refs, replace_refs], altered)

    # For latex/pdf, inject command to change figurename
    if fmt == 'latex' and figurename != 'Figure':
        tex = r'\renewcommand{\figurename}{%s}'%figurename
        altered[1] = [RawBlock('tex', tex)] + altered[1]

    # For latex/pdf, inject a command to fake \cref when it is missing
    if include_cref and fmt == 'latex':
        tex1 = r'\providecommand{\cref}{%s~\ref}' % figureabbrev
        tex2 = r'\providecommand{\Cref}{%s~\ref}' % figurelong
        altered[1] = [RawBlock('tex', tex1), RawBlock('tex', tex2)] + altered[1]

    # Dump the results
    json.dump(altered, STDOUT)

    # Flush stdout
    STDOUT.flush()

if __name__ == '__main__':
    main()
