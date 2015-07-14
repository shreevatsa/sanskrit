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
import itertools
import json
import logging
import os.path
import re
import tempfile

import print_utils
import read.filters
import simple_identifier


def Print(x):
  return print_utils.Print(x)


def Timestamp():
  return datetime.datetime.strftime(datetime.datetime.now(),
                                    '%Y-%m-%d.%H:%M:%S')


def SplitIntoVerses(input_lines):
  """Try to return a list of verses, from the lines."""
  lines_new = []
  last_seen_verse_number = -1
  for line in input_lines:
    match = re.match(r'^MSS_(\d+)-\d+', line)
    if match:
      current_verse_number = match.group(1)
      if current_verse_number != last_seen_verse_number:
        last_seen_verse_number = current_verse_number
        lines_new.append('')
      # line = line[len(match.group(0)):]
    lines_new.append(line)

  verses_found = []
  for key, group in itertools.groupby(lines_new, bool):
    if key:
      verses_found.append(list(group))
  return verses_found


def IgnoreLine(text):
  # Line enclosed in round brackets
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
  argument_parser.add_argument('--break_at_error', action='store_true',
                               help='Whether to break as soon as one imperfect'
                               ' verse is found.')
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
    l = read.filters.process_html(l)
    l = l.strip()
    if IgnoreLine(l):
      continue
    if seen_separators < 2 and re.search('<![-]{50,}->', l):
      seen_separators += 1
    elif seen_separators == 2 and not l.startswith('<'):
      l =  read.filters.remove_verse_numbers(l)
      lines.extend(l.splitlines())

  verses = SplitIntoVerses(lines)
  verses = [verse for verse in verses if AcceptVerse(verse)]

  identifier = simple_identifier.SimpleIdentifier()
  table = {}
  for (verse_number, verse) in enumerate(verses):
    verse = [verse_line.strip() for verse_line in verse]
    ok_and_results = identifier.IdentifyFromLines(verse)
    if not ok_and_results:      # None for lines that contain no syllables
      continue
    (perfect, results) = ok_and_results
    if not results:
      table['unknown'] = table.get('unknown', 0) + 1
      if args.print_unidentified_verses != 'none':
        Print('Verse %4d:' % (verse_number + 1))
        if args.print_unidentified_verses == 'full':
          Print('\n'.join(verse))
          Print(identifier.AllDebugOutput())
          Print('')
      continue

    # We've dealt with the case where there are no results
    assert results
    assert isinstance(results, list)
    metre_name = results[0]
    if args.print_identified_verses != 'none':
      Print('Verse %4d is%sin %s' % (
          verse_number + 1,
          ' ' if perfect else ' probably ',
          metre_name))
      if args.print_identified_verses == 'full':
        Print('\n'.join(verse))
    table[metre_name] = table.get(metre_name, 0) + 1
    if not perfect and args.break_at_error:
      Print('\n'.join(verse))
      Print(identifier.AllDebugOutput())
      Print('')
      break

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
