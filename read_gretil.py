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


if __name__ == '__main__':
  logger = logging.getLogger()
  handler = logging.FileHandler('/var/tmp/read_gretil.log')
  handler.setFormatter(
      logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
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
  verses = [verse for verse in verses if verse != ['{ūttarameghaḥ}']]

  for (verse_number, verse) in enumerate(verses):
    verse = [l.strip() for l in verse]
    identifier = sscan.Identifier()
    metre = identifier.IdentifyFromLines(verse)
    if metre:
      result = ''
      if isinstance(metre, list):
        result = ' or '.join(set(m.MetreName() + ' (probably)' for m in metre))
      else:
        result = metre.MetreName()
      print(('Verse %4d is in %s' % (verse_number + 1, result)).encode('utf8'))
    if not metre:  # or isinstance(metre, list):
      print('Verse %4d:' % (verse_number + 1))
      print('\n'.join(verse).encode('utf8'))
      print(identifier.AllDebugOutput().encode('utf8'))
      print('')
