#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Reads from a GRETIL UTF-8 encoded HTML file."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import argparse
import codecs
import datetime
import json
import logging
import os.path
import re
import tempfile

import handle_input
import print_utils
import simple_identifier


def Print(x):
  return print_utils.Print(x)


def Timestamp():
  return datetime.datetime.strftime(datetime.datetime.now(),
                                    '%Y-%m-%d.%H:%M:%S')


def IgnoreLine(text):
  if re.match('^[(].*[)]$', text):
    return True
  if text.startswith(r'\footnote'):
    return True
  return False


def AcceptVerse(v):
  """Checks that the verse is not in one of a number of known bad patterns."""
  if len(v) == 1:
    line = v[0]
    assert isinstance(line, unicode)
    if line in ['{ūttarameghaḥ}', 'iti śubhaṃ bhūyāt |']:
      return False
    if line.startswith('iti'):
      return False
    if line.startswith('atha'):
      return False
  return True


if __name__ == '__main__':
  argument_parser = argparse.ArgumentParser(description='Read a GRETIL file, '
                                            'identify verses and their metres, '
                                            'and generate statistics.')
  argument_parser.add_argument('input_file', type=unicode,
                               help='A file containing list of verses')
  argument_parser.add_argument('--print_identified_verses',
                               choices=['none', 'brief', 'full'],
                               default='brief',
                               help='What to print when the metre of a verse is'
                               ' identified: nothing, just the metre, or'
                               ' the whole verse')
  argument_parser.add_argument('--print_unidentified_verses',
                               choices=['none', 'brief', 'full'],
                               default='full',
                               help='What to print when a verse is not in any'
                               ' known metre: nothing, just a message,'
                               ' or the whole verse')
  args = argument_parser.parse_args()
  input_file_name = args.input_file

  logger = logging.getLogger()
  log_file = tempfile.NamedTemporaryFile(prefix='read_gretil_%s_' %
                                         os.path.basename(input_file_name),
                                         delete=False)
  Print('Logging to %s' % log_file.name)
  handler = logging.FileHandler(log_file.name)
  handler.setFormatter(logging.Formatter(
      '%(levelname)s	%(asctime)s %(filename)s:%(lineno)d] %(message)s'))
  logger.addHandler(handler)
  logger.setLevel(logging.DEBUG)

  lines = []
  seen_separators = 0
  for l in codecs.open(input_file_name, 'r', 'utf-8'):
    assert isinstance(l, unicode)
    l = handle_input.RemoveHTML(l)
    l = l.strip()
    if IgnoreLine(l):
      continue
    if seen_separators < 2 and re.search('<![-]{50,}->', l):
      seen_separators += 1
    elif seen_separators == 2 and not l.startswith('<'):
      (l, n) = handle_input.RemoveVerseNumber(l)
      lines.append(l)
      if n:
        lines.append('')

  verses = handle_input.BreakIntoVerses(lines)
  verses = [verse for verse in verses if AcceptVerse(verse)]

  identifier = simple_identifier.SimpleIdentifier()
  table = {}
  for (verse_number, verse) in enumerate(verses):
    verse = [l.strip() for l in verse]
    metre = identifier.IdentifyFromLines(verse)
    if not metre:
      clean = identifier.cleaned_output[1:]
      if not ''.join(clean):
        continue
      table['unknown'] = table.get('unknown', 0) + 1
      if args.print_unidentified_verses != 'none':
        Print('Verse %4d:' % (verse_number + 1))
        if args.print_unidentified_verses == 'full':
          Print('\n'.join(verse))
          Print(identifier.AllDebugOutput())
          Print('')
      continue

    # We've dealt with the case where there are no results
    assert metre
    assert isinstance(metre, list)
    metre_name = None
    if len(metre) == 1 and not metre[0].issues:
      # The best possible case
      metre_name = metre[0].MetreName()
      if args.print_identified_verses != 'none':
        Print('Verse %4d is in %s' % (verse_number + 1, metre_name))
        if args.print_identified_verses == 'full':
          Print('\n'.join(verse))
    else:
      all_metres = set(m.MetreNameOnlyBase() for m in metre)
      # assert len(all_metres) == 1, (all_metres, verse)
      metre_name = all_metres.pop()
      if args.print_identified_verses != 'none':
        Print('Verse %4d is in %s (probably), but it has issues'
              % (verse_number + 1, metre_name))
        if args.print_identified_verses == 'full':
          Print('\n'.join(verse))
    # Either way, metre_name should be set by now
    assert metre_name is not None
    table[metre_name] = table.get(metre_name, 0) + 1

  sum_counts = sum(value for (key, value) in table.items())
  for (metre, count) in table.items():
    table[metre] = [count, '%.2f%%' % (count * 100 / sum_counts)]
  Print(table)

  stats_file_name = os.path.basename(input_file_name) + '.stats'
  stats_file = codecs.open(stats_file_name, 'w', 'utf-8')
  json.dump(table, stats_file, indent=2, ensure_ascii=False,
            separators=(',', ': '))
  stats_file.close()
  stats_file = codecs.open(stats_file_name, 'r', 'utf-8')
  assert table == json.load(stats_file, 'utf-8')
