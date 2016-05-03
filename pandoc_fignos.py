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
#
# There is also an initial scan to do some preprocessing.

# pylint: disable=invalid-name

import re
import functools
import sys
import argparse
import json

from pandocfilters import walk
from pandocfilters import RawBlock, RawInline
from pandocfilters import Str, Para, Plain, elt

import pandocfiltering
from pandocfiltering import repair_refs, extract_attrs, pandocify
from pandocfiltering import filter_null
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

# Detect python 3
PY3 = sys.version_info > (3,)

# Url-encoded strings are handled in different packages in python 2 and 3
# pylint: disable=no-name-in-module
if PY3:
    from urllib.request import unquote
else:
    from urllib import unquote

# Patterns for matching labels and references
LABEL_PATTERN = re.compile(r'(fig:[\w/-]*)')
REF_PATTERN = re.compile(r'@(fig:[\w/-]+)')

references = {}  # Global references tracker

# Meta variables; may be reset by main()
figurename = 'Figure'
cref = False


# Helper functions ----------------------------------------------------------

def is_figref(key, value):
    """True if this is a figure reference; False otherwise."""
    return key == 'Cite' and REF_PATTERN.match(value[1][0]['c']) and \
       parse_figref(value)[1] in references

def parse_figref(value):
    """Parses a figure reference."""
    prefix = value[0][0]['citationPrefix']
    label = REF_PATTERN.match(value[1][0]['c']).group(1)
    suffix = value[0][0]['citationSuffix']
    return prefix, label, suffix

def is_attrimage(key, value):
    """True if this is an attributed image; False otherwise."""
    return key == 'Image' and len(value) == 3

def parse_attrimage(value):
    """Parses an attributed image."""
    attrs, caption, target = value
    if attrs[0] == 'fig:': # Make up a unique description
        attrs[0] = 'fig:' + '__'+str(hash(target[0]))+'__'
    return attrs, caption, target

def add_figure_marker(key, value):
    """Adds figure marker to the image."""
    assert is_attrimage(key, value)
    # pylint: disable=unused-variable
    attrs, caption, target = parse_attrimage(value)
    target[1] = 'fig:'  # Pandoc uses this as a figure marker

def is_figure(key, value):
    """True if this is a figure; False otherwise."""
    if key == 'Para' and len(value) == 1:
        return is_figure(value[0]['t'], value[0]['c'])  # Recursive call
    elif key == 'Image' and is_attrimage(key, value):
        # pylint: disable=unused-variable
        attrs, caption, target = parse_attrimage(value)
        return target[1] == 'fig:'  # Pandoc uses this as a figure marker
    else:
        return False


# preprocess() ---------------------------------------------------------------

def preprocess(key, value, fmt, meta):  # pylint: disable=unused-argument
    """Preprocesses to correct for problems."""
    if key in ('Para', 'Plain'):
        repair_refs(value)


# replace_attrimages() and friends -------------------------------------------

def extract_imageattrs(value, n):
    """Extracts attributes from a list of values.  n is the index of the image.
    Extracted elements are set to None in the value list.  Attrs are returned
    in pandoc format.
    """
    assert value[n]['t'] == 'Image'

    # Notes: No space between an image and its attributes;
    # extract_attrs() sets extracted values to None in the value list.
    try:
        return extract_attrs(value, n+1)
    except AssertionError:
        if PANDOCVERSION < '1.16':
            # Look for attributes attached to the image path, as occurs with
            # reference links.  Remove the encoding.
            image = value[n]
            try:
                seq = unquote(image['c'][1][0]).split()
                path, s = seq[0], ' '.join(seq[1:])
            except ValueError:
                pass
            else:
                image['c'][1][0] = path  # Remove attr string from the path
                return PandocAttributes(s.strip(), 'markdown').to_pandoc()

@filter_null
def use_attrimages(value):
    """Internally use AttrImage for all attributed images.
    Unattributed images are left untouched.
    """
    # Seach for attributed images and replace them with an AttrImage
    for i, v in enumerate(value):
        if v and v['t'] == 'Image':
            attrs = extract_imageattrs(value, i)  # Nullifies extracted values
            if attrs:
                value[i] = AttrImage(attrs, *v['c'])

def replace_attrimages(key, value, fmt, meta): # pylint: disable=unused-argument
    """Replaces attributed images while storing reference labels."""

    if key == 'Para':

        # Always use AttrImage internally
        if PANDOCVERSION < '1.16':  # Attributed images were introduced in 1.16
            use_attrimages(value)
            if len(value) == 1 and value[0]['t'] == 'Image':
                # Add the figure marker
                add_figure_marker(value[0]['t'], value[0]['c'])

        # Prepend html anchors for figures.
        if fmt in ('html', 'html5') and is_figure(key, value):
            attrs, caption, target = parse_attrimage(value[0]['c'])
            anchor = RawInline('html', '<a name="%s"></a>'%attrs[0])
            return [Plain([anchor]), Para(value)]

    elif is_attrimage(key, value):

        # Parse the image
        attrs, caption, target = parse_attrimage(value)

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
        if PANDOCVERSION < '1.16':  # Attributed images are not supported
            return Image(caption, target)
        else:
            if PANDOCVERSION >= '1.17' and fmt == 'latex':
                # Remove id from the image attributes.  It is incorrectly
                # handled by pandoc's TeX writer for these versions
                if attrs[0].startswith('fig:'):
                    attrs[0] = ''
            return AttrImage(attrs, caption, target)


# replace_refs() and friends -------------------------------------------------

@filter_null
def use_attrrefs(value):
    """Extracts attributes appends them to the reference."""
    for i, v in enumerate(value):
        if v and is_figref(v['t'], v['c']):
            if i+1 < len(value):
                try:
                    # extract_attrs() sets extracted values to None in the
                    # value list.
                    attrs = extract_attrs(value, i+1)
                    # Temporarily append attributes to reference
                    v['c'].append(attrs)
                except AssertionError:
                    pass

def is_braced_figref(value, i):
    """Returns true if a reference is braced; otherwise False.
    i is the index in the value list.
    """
    # The braces will be found in the surrounding values
    return is_figref(value[i]['t'], value[i]['c']) \
      and value[i-1]['t'] == 'Str' and value[i+1]['t'] == 'Str' \
      and value[i-1]['c'].endswith('{') and value[i+1]['c'].startswith('}')

@filter_null
def remove_braces_from_figrefs(value):
    """Search for figure references and remove curly braces around them."""
    for i in range(1, len(value)-1):
        if is_braced_figref(value, i):
            if len(value[i-1]['c']) > 1:
                value[i-1]['c'] = value[i-1]['c'][:-1]
            else:
                value[i-1] = None
            if len(value[i+1]['c']):
                value[i+1]['c'] = value[i+1]['c'][1:]
            else:
                value[i+1] = None

# pylint: disable=unused-argument
def replace_refs(key, value, fmt, meta):
    """Replaces references to labelled images."""

    if key in ('Para', 'Plain'):
        use_attrrefs(value)
        remove_braces_from_figrefs(value)

    elif is_figref(key, value):

        # Parse the figure reference
        prefix, label, suffix = parse_figref(value)

        # Get attributes for this reference
        attrs = PandocAttributes(value.pop(-1), 'pandoc') if len(value) == 3 \
          else PandocAttributes('', 'markdown')

        # Interpret the attributes
        cref_ = cref
        onvals = ['On', 'True', 'Yes']
        if 'cref' in attrs.kvs:
            cref_ = True if attrs['cref'].capitalize() in onvals else False
        capitalize = False
        if 'Cref' in attrs.kvs:
            if attrs['Cref'].capitalize() in onvals:
                cref_ = True
                capitalize = True

        # The replacement depends on the output format
        if fmt == 'latex':
            if cref_:
                macro = r'\Cref' if capitalize else r'\cref'
                rawinline = [RawInline('tex', r'%s{%s}'%(macro, label))]
                return prefix + rawinline + suffix
            else:
                return prefix + [RawInline('tex', r'\ref{%s}'%label)] + suffix
        elif fmt in ('html', 'html5'):
            link = '<a href="#%s">%s</a>' % (label, references[label])
            return prefix + [RawInline('html', link)] + suffix
        else:
            return prefix + [Str('%d'%references[label])] + suffix


# Main program ---------------------------------------------------------------

def main():
    """Filters the document AST."""

    # pylint: disable=global-statement
    global figurename, cref

    # Get the output format, document and metadata
    fmt = args.fmt
    doc = json.loads(STDIN.read())
    meta = doc[0]['unMeta']

    # Extract meta variables
    if 'figure-name' in meta:
        figurename = meta['figure-name']['c']  # Works for cmdline vars
        if type(figurename) is list:  # For YAML vars
            # Note: At this point I am expecting a single-word replacement.
            # This will need to be revisited if multiple words are needed.
            figurename = figurename[0]['c']
    if 'cref' in meta and meta['cref']['c']:
        cref = True
    if 'fignos-cref' in meta and meta['fignos-cref']:
        cref = True

    # Replace attributed images and references in the AST
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [preprocess, replace_attrimages, replace_refs],
                               doc)

    # For latex/pdf, inject command to change figurename
    if fmt == 'latex' and figurename != 'Figure':
        tex = r'\renewcommand{\figurename}{%s}'%figurename
        altered[1] = [RawBlock('tex', tex)] + altered[1]

    # For latex/pdf, inject a command to ensure \cref
    if fmt == 'latex' and cref:
        tex1 = r'\providecommand{\cref}{\ref}'
        tex2 = r'\providecommand{\Cref}{\ref}'
        altered[1] = [RawBlock('tex', tex1), RawBlock('tex', tex2)] + altered[1]

    # Dump the results
    json.dump(altered, STDOUT)

    # Flush stdout
    STDOUT.flush()

if __name__ == '__main__':
    main()
