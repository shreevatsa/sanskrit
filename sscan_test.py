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
  if verse == ['{UttarameghaH}']:
    continue
  assert len(verse) == 4, verse
  counter += 1

  print('Verse %d: ' % counter)
  print('\n\t\t\t\t\t\t'.join([''] + verse))
  identifier = sscan.Identifier()
  identifier.IdentifyFromLines(verse)
  print('\n'.join(identifier.output))
  print()
