from __future__ import unicode_literals

import sys

import handle_input
import sscan

lines = [l.strip() for l in sys.stdin.readlines()]
counter = 0
for verse_lines in handle_input.BreakIntoVerses(lines):
  if verse_lines == ['{UttarameghaH}']:
    continue
  assert len(verse_lines) == 4, verse_lines
  counter += 1

  print 'Verse %d: ' % counter
  print '\n\t\t\t\t\t\t'.join([''] + verse_lines)
  sscan.InitializeData()
  sscan.IdentifyFromLines(verse_lines)
  print
