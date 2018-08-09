#! /usr/bin/env python3

"""A pandoc filter that saves the json pandoc provides to saved.json.

e.g.: pandoc test.md --filter ./savejson.py

"""

# Copyright 2016 Thomas J. Duck.
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

import json

from pandocxnos import STDIN, STDOUT

def main():
    """Main program"""

    doc = json.loads(STDIN.read())

    with open('saved.json', 'w') as f:
        json.dump(doc, f)

    json.dump(doc, STDOUT)
    STDOUT.flush()

if __name__ == '__main__':
    main()
