#! /usr/bin/env python

"""pandoc-fignos: a pandoc filter that inserts figure nos. and refs."""

# Copyright 2015 Thomas J. Duck.
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
# The basic idea is to scan the AST twice in order to:
#
#   1. Insert text for the figure number in each figure caption.
#      For LaTeX, insert \label{...} instead.  The figure labels
#      and associated figure numbers are stored in the global
#      references tracker.
#
#   2. Replace each reference with a figure number.  For LaTeX,
#      replace with \ref{...} instead.
#
#

import re
import functools
import itertools
import io
import sys

# pylint: disable=import-error
import pandocfilters
from pandocfilters import stringify, walk
from pandocfilters import RawInline, Str, Space, Image, Para, Plain
from pandocattributes import PandocAttributes

# Patterns for matching labels and references
LABEL_PATTERN = re.compile(r'(fig:[\w/-]*)(.*)')
REF_PATTERN = re.compile(r'@(fig:[\w/-]+)')

# Detect python 3
PY3 = sys.version_info > (3,)

# Pandoc uses UTF-8 for both input and output; so must we
if PY3:  # Force utf-8 decoding (decoding of input streams is automatic in py3)
    STDIN = io.TextIOWrapper(sys.stdin.buffer, 'utf-8', 'strict')
    STDOUT = io.TextIOWrapper(sys.stdout.buffer, 'utf-8', 'strict')
else:    # No decoding; utf-8-encoded strings in means the same out
    STDIN = sys.stdin
    STDOUT = sys.stdout

# pylint: disable=invalid-name
references = {}  # Global references tracker

def is_attrimage(key, value):
    """True if this is an attributed image; False otherwise."""
    try:
        s = stringify(value[1:]).strip()
        return key == 'Para' and value[0]['t'] == 'Image' \
            and s.startswith('{') and s.endswith('}')
    # pylint: disable=bare-except
    except:
        return False

def parse_attrimage(value):
    """Parses an attributed image."""
    caption, target = value[0]['c']
    s = stringify(value[1:]).strip() # The attribute string
    # Extract label from attributes (label, classes, kvs)
    label = PandocAttributes(s, 'markdown').to_pandoc()[0]
    if label == 'fig:': # Make up a unique description
        label = label + '__'+str(hash(target[0]))+'__'
    return caption, target, label

def is_ref(key, value):
    """True if this is a figure reference; False otherwise."""
    return key == 'Cite' and REF_PATTERN.match(value[1][0]['c']) and \
            parse_ref(value)[1] in references

def parse_ref(value):
    """Parses a figure reference."""
    prefix = value[0][0]['citationPrefix']
    label = REF_PATTERN.match(value[1][0]['c']).groups()[0]
    suffix = value[0][0]['citationSuffix']
    return prefix, label, suffix

def ast(string):
    """Returns an AST representation of the string."""
    toks = [Str(tok) for tok in string.split()]
    spaces = [Space()]*len(toks)
    ret = list(itertools.chain(*zip(toks, spaces)))
    if string[0] == ' ':
        ret = [Space()] + ret
    return ret if string[-1] == ' ' else ret[:-1]

def replace_attrimages(key, value, fmt, meta):
    """Replaces attributed images while storing reference labels."""

    if is_attrimage(key, value):

        # Parse the image
        caption, target, label = parse_attrimage(value)

        # Bail out if the label does not conform
        if not label or not LABEL_PATTERN.match(label):
            return None

        # Save the reference
        references[label] = len(references) + 1

        # Adjust caption depending on the output format
        if fmt == 'latex':
            caption = list(caption) + [RawInline('tex', r'\label{%s}'%label)]
        else:
            caption = ast('Figure %d. '%references[label]) + list(caption)

        # Retain the attributes, if requested
        keepattrs = meta['fignos-keepattrs']['c'] \
          if 'fignos-keepattrs' in meta else False
        attributes = value[1:] if keepattrs else []

        # Required for pandoc to process the image
        target[1] = "fig:"

        # Return the replacement
        if fmt == 'html' or fmt == 'html5':
            anchor = RawInline('html', '<a name="%s"></a>'%label)
            return [Plain([anchor]),
                    Para([Image(caption, target)] + attributes)]
        else:
            return Para([Image(caption, target)] + attributes)

# pylint: disable=unused-argument
def replace_refs(key, value, fmt, meta):
    """Replaces references to labelled images."""

    # Search for references in paras and remove curly braces around them
    if key == 'Para':
        flag = False
        # Search
        for i, elem in enumerate(value):
            k, v = elem['t'], elem['c']
            if is_ref(k, v) and i > 0 and i < len(value)-1 \
              and value[i-1]['t'] == 'Str' and value[i+1]['t'] == 'Str' \
              and value[i-1]['c'].endswith('{') \
              and value[i+1]['c'].startswith('}'):
                flag = True  # Found reference
                value[i-1]['c'] = value[i-1]['c'][:-1]
                value[i+1]['c'] = value[i+1]['c'][1:]
        return Para(value) if flag else None

    # Replace references
    if is_ref(key, value):
        prefix, label, suffix = parse_ref(value)
        # The replacement depends on the output format
        if fmt == 'latex':
            return prefix + [RawInline('tex', r'\ref{%s}'%label)] + suffix
        elif fmt == 'html' or fmt == 'html5':
            link = '<a href="#%s">%s</a>' % (label, references[label])
            return prefix + [RawInline('html', link)] + suffix
        else:
            return prefix + [Str('%d'%references[label])] + suffix

def main():
    """Filters the document AST."""

    # Get the output format, document and metadata
    fmt = sys.argv[1] if len(sys.argv) > 1 else ''
    doc = pandocfilters.json.loads(STDIN.read())
    meta = doc[0]['unMeta']

    # Replace attributed images and references in the AST
    altered = functools.reduce(lambda x, action: walk(x, action, fmt, meta),
                               [replace_attrimages, replace_refs], doc)

    # Dump the results
    pandocfilters.json.dump(altered, STDOUT)


if __name__ == '__main__':
    main()
