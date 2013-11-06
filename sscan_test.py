from __future__ import unicode_literals

import itertools
import sys

import sscan


def BreakIntoVerses(input_lines):
  verses = []
  for key, group in itertools.groupby(input_lines, bool):
    if not key:
      continue
    verses.append(list(group))
  return verses

lines = [l.strip() for l in sys.stdin.readlines()]
counter = 0
for verse_lines in BreakIntoVerses(lines):
  counter += 1
  if verse_lines == ['{UttarameghaH}']:
    continue
  assert len(verse_lines) == 4, verse_lines

  print 'Verse %d: ' % counter
  print '\n\t\t\t\t\t\t'.join([''] + verse_lines)
  sscan.InitializeData()
  sscan.IdentifyFromLines(verse_lines)
  print
