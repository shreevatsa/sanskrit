#!/usr/bin/python

"""Reads from a GRETIL UTF-8 encoded HTML file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import sys

import handle_input
import sscan


if __name__ == '__main__':
  lines = []
  seen_separators = 0
  for l in sys.stdin:
    l = l.decode('utf8')
    l = handle_input.RemoveHTML(l)
    l = l.strip()
    if seen_separators < 2 and re.search('<![-]{50,}->', l):
      seen_separators += 1
    elif seen_separators == 2 and not l.startswith('<'):
      (l, n) = handle_input.RemoveVerseNumber(l)
      lines.append(l)
      if n:
        lines.append('')

  verses = handle_input.BreakIntoVerses(lines)
  for verse in verses:
    print('\n\t\t\t\t\t\t'.join([''] + verse).encode('utf8'))
    verse = [l.strip() for l in verse]
    identifier = sscan.Identifier()
    identifier.IdentifyFromLines(verse)
    print('\n'.join(identifier.output).encode('utf8'))
    print('')
