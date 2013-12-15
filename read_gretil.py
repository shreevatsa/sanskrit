#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Reads from a GRETIL UTF-8 encoded HTML file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re
import sys

import handle_input
import sscan


def Print(u):
  assert isinstance(u, unicode)
  print(u.encode('utf8'))

if __name__ == '__main__':
  logger = logging.getLogger()
  handler = logging.FileHandler('/var/tmp/read_gretil.log')
  handler.setFormatter(logging.Formatter(
      '%(levelname)s	%(asctime)s %(filename)s:%(lineno)d] %(message)s'))
  logger.addHandler(handler)
  logger.setLevel(logging.DEBUG)

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
  known_non_verses = [['{ūttarameghaḥ}'], ['iti śubhaṃ bhūyāt |']]
  verses = [verse for verse in verses if verse not in known_non_verses]

  identifier = sscan.Identifier()
  for (verse_number, verse) in enumerate(verses):
    verse = [l.strip() for l in verse]
    metre = identifier.IdentifyFromLines(verse)
    if not metre:
      clean = identifier.cleaned_output[1:]
      if not ''.join(clean):
        continue
      Print('Verse %4d:' % (verse_number + 1))
      Print('\n'.join(verse))
      Print(identifier.AllDebugOutput())
      Print('')
      continue
    assert metre
    assert isinstance(metre, list)
    if len(metre) == 1 and not metre[0].issues:
      Print('Verse %4d is in %s' % (verse_number + 1, metre[0].MetreName()))
    else:
      all_metres = set(m.MetreNameOnlyBase() for m in metre)
      assert len(all_metres) == 1, (all_metres, verse)
      Print('Verse %4d is in %s (probably), but it has issues'
            % (verse_number + 1, all_metres.pop()))
