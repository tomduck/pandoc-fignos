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

import re
import functools
import argparse
import json
import uuid

import sys
if sys.version_info > (3,):
    from urllib.request import unquote  # pylint: disable=no-name-in-module
else:
    from urllib import unquote  # pylint: disable=no-name-in-module

from pandocfilters import walk, elt
from pandocfilters import Image, Math, Str, Space, Para, RawBlock, RawInline

import pandocxnos
from pandocxnos import STRTYPES, STDIN, STDOUT
from pandocxnos import get_meta, extract_attrs
from pandocxnos import repair_refs, process_refs_factory, replace_refs_factory
from pandocxnos import attach_attrs_factory, detach_attrs_factory

from pandocattributes import PandocAttributes


# Read the command-line arguments
parser = argparse.ArgumentParser(description='Pandoc figure numbers filter.')
parser.add_argument('fmt')
parser.add_argument('--pandocversion', help='The pandoc version.')
args = parser.parse_args()

# Initialize pandocxnos
PANDOCVERSION = pandocxnos.init(args.pandocversion)

# Override the Image element for pandoc < 1.16
if PANDOCVERSION < '1.16':
    Image = elt('Image', 2)

# Pattern for matching labels
LABEL_PATTERN = re.compile(r'(fig:[\w/-]*)')

Nreferences = 0  # The numbered references count (i.e., excluding tags)
references = {}  # Global references tracker

# Meta variables; may be reset elsewhere
captionname = 'Figure'            # Used with \figurename
plusname = ['fig.', 'figs.']      # Used with \cref
starname = ['Figure', 'Figures']  # Used with \Cref
cleveref_default = False          # Default setting for clever referencing


# Actions --------------------------------------------------------------------

def _extract_attrs(x, n):
    """Extracts attributes for an image.  n is the index where the
    attributes begin.  Extracted elements are deleted from the element
    list x.  Attrs are returned in pandoc format.
    """
    try:
        return extract_attrs(x, n)

    except (ValueError, IndexError):
        # Look for attributes attached to the image path, as occurs with
        # reference links.  Remove the encoding.
        assert x[n-1]['t'] == 'Image'
        image = x[n-1]
        path, attrs = unquote(image['c'][-1][0]).split(' ', 1)
        if attrs:
            image['c'][-1][0] = path  # Remove attr string from the path
            return PandocAttributes(attrs.strip(), 'markdown').to_pandoc()
        else:
            raise

attach_attrs_image = attach_attrs_factory(Image, extract_attrs=_extract_attrs)
detach_attrs_image = detach_attrs_factory(Image)

def _store_ref(attrs):
    """Stores the reference in the global references tracker.
    Returns True if this is a tagged table; False otherwise."""

    # pylint: disable=global-statement
    global Nreferences

    attrs = PandocAttributes(attrs, 'pandoc')
    if 'tag' in attrs.kvs:
        # Remove any surrounding quotes
        if attrs['tag'][0] == '"' and attrs['tag'][-1] == '"':
            attrs['tag'] = attrs['tag'].strip('"')
        elif attrs['tag'][0] == "'" and attrs['tag'][-1] == "'":
            attrs['tag'] = attrs['tag'].strip("'")
        references[attrs.id] = attrs['tag']
    else:
        Nreferences += 1
        references[attrs.id] = Nreferences
    return 'tag' in attrs.kvs

def _process_image(value, fmt):
    """Processes the image."""

    # Parse the image
    attrs, caption = value[:2]

    # Bail out if the label does not conform
    if not attrs[0] or not LABEL_PATTERN.match(attrs[0]):
        return True, None, None

    if attrs[0] == 'fig:': # Make up a unique description
        attrs[0] = attrs[0] + str(uuid.uuid4())

    # Save the reference
    is_tagged = _store_ref(attrs)

    # Adjust caption depending on the output format
    if fmt == 'latex':
        value[1] += [RawInline('tex', r'\label{%s}'%attrs[0])]
    elif type(references[attrs[0]]) is int:
        value[1] = [Str(captionname), Space(),
                    Str('%d:'%references[attrs[0]]), Space()] + list(caption)
    else:  # It is a string
        assert type(references[attrs[0]]) in STRTYPES
        # Handle both math and text
        text = references[attrs[0]]
        if text.startswith('$') and text.endswith('$'):
            math = text.replace(' ', r'\ ')[1:-1]
            els = [Math({"t":"InlineMath", "c":[]}, math), Str(':')]
        else:
            els = [Str(text+':')]
        value[1] = [Str('Table'), Space()]+ els + [Space()] + list(caption)

    return False, is_tagged, attrs

def process_figures(key, value, fmt, meta): # pylint: disable=unused-argument
    """Processes the figures."""

    if key == 'Para' and len(value) == 1:  # May enclose a Figure
        if value[0]['t'] == 'Image' and len(value[0]['c']) == 3 and \
          value[0]['c'][2][1] == 'fig:':   # It does!

            # Process the image
            bail, is_tagged, attrs = _process_image(value[0]['c'], fmt)
            if bail:
                return

            # Context-dependent output
            if fmt == 'latex':
                label = attrs[0]
                if PANDOCVERSION >= '1.17':
                    # Remove id from the image attributes.  It is incorrectly
                    # handled by pandoc's TeX writer for these versions
                    if LABEL_PATTERN.match(attrs[0]):
                        attrs[0] = ''
                if is_tagged:  # Code in the tags
                    tex = '\n'.join([r'\let\oldthefigure=\thefigure',
                                     r'\renewcommand\thefigure{%s}'%\
                                     references[label]])
                    pre = RawBlock('tex', tex)
                    # pylint: disable=star-args
                    figure = elt('Image', 3)(*(value[0]['c']))
                    figure['c'] = list(figure['c'])  # Needed for attr filtering
                    tex = '\n'.join([r'\let\thefigure=\oldthefigure',
                                     r'\addtocounter{figure}{-1}'])
                    post = RawBlock('tex', tex)
                    return [pre, Para(value), post]
            elif fmt in ('html', 'html5'):  # Insert anchor
                # pylint: disable=unused-variable
                attrs, caption, target = value[0]['c']
                if LABEL_PATTERN.match(attrs[0]):
                    anchor = RawBlock('html', '<a name="%s"></a>'%attrs[0])
                    return [anchor, Para(value)]


# Main program ---------------------------------------------------------------

def process(meta):
    """Saves metadata fields in global variables and returns a few
    computed fields."""

    # pylint: disable=global-statement
    global captionname, cleveref_default, plusname, starname

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

    if 'fignos-star-name' in meta:
        tmp = get_meta(meta, 'fignos-star-name')
        if type(tmp) is list:
            starname = tmp
        else:
            starname[0] = tmp
        assert len(starname) == 2
        for name in starname:
            assert type(name) in STRTYPES


def main():
    """Filters the document AST."""

    # Get the output format, document and metadata
    fmt = args.fmt
    doc = json.loads(STDIN.read())
    meta = doc[0]['unMeta']

    # Process the metadata variables
    process(meta)

    # First pass
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [attach_attrs_image, process_figures,
                                detach_attrs_image], doc)

    # Second pass
    process_refs = process_refs_factory(references.keys())
    replace_refs = replace_refs_factory(references, cleveref_default,
                                        plusname, starname, 'figure')
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [repair_refs, process_refs, replace_refs],
                               altered)


    # Assemble supporting TeX
    if fmt == 'latex':
        tex = ['% Fignos directives']

        # Change caption name
        if captionname != 'Figure':
            tex.append(r'\renewcommand{\figurename}{%s}'%captionname)

        if len(tex) > 1:
            altered[1] = [RawBlock('tex', '\n'.join(tex))] + altered[1]

    # Dump the results
    json.dump(altered, STDOUT)

    # Flush stdout
    STDOUT.flush()

if __name__ == '__main__':
    main()
