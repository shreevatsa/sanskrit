"""Tests the metre identifier by running it on a text."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys

import handle_input
import sscan

lines = [l.strip() for l in sys.stdin.readlines()]
counter = 0
verses = handle_input.BreakIntoVerses(lines)
for verse in verses:
  assert verse
  if verse == ['{UttarameghaH}']:
    continue
  assert len(verse) == 4, verse
  counter += 1

  identifier = sscan.Identifier()
  print('Verse %d: ' % counter)
  metre = identifier.IdentifyFromLines(verse)
  if metre:
    print(metre.encode('utf8'))
  else:
    print('\n\t\t\t\t\t\t'.join([''] + verse))
    print(identifier.AllDebugOutput().encode('utf8'))
    print()
