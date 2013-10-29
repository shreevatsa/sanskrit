import itertools
import sys

import sscan

lines = [l.strip() for l in sys.stdin.readlines()]
counter = 0
for key, group in itertools.groupby(lines, bool):
  if not key:
    continue
  counter += 1
  verse_lines = list(group)
  if verse_lines == ['{UttarameghaH}']:
    continue
  assert len(verse_lines) == 4, verse_lines

  print 'Verse %d: ' % counter
  print '\n\t\t\t\t\t\t'.join([''] + verse_lines)
  sscan.InitializeData()
  sscan.IdentifyFromLines(verse_lines)
  print
