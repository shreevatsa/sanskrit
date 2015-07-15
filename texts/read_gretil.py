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

from print_utils import Print
import read.filters
import identifier_pipeline


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


def get_args():
  """Setting up argument parser and parsing passed arguments."""
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
  return argument_parser.parse_args()


def set_up_logger(input_file_name):
  logger = logging.getLogger()
  log_file = tempfile.NamedTemporaryFile(prefix='read_gretil_%s_' %
                                         os.path.basename(input_file_name),
                                         delete=False)
  Print('Logging to %s' % log_file.name)
  handler = logging.FileHandler(log_file.name)
  handler.setFormatter(logging.Formatter(
      '%(levelname)s\t%(asctime)s %(filename)s:%(lineno)d] %(message)s'))
  logger.addHandler(handler)
  logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
  args = get_args()
  input_file_name = args.input_file
  set_up_logger(input_file_name)

  text = codecs.open(input_file_name, 'r', 'utf-8').read()

  text = read.filters.process_crlf(text)
  text = read.filters.normalize_nfkc(text)
  text = read.filters.remove_control_characters(text)
  text = read.filters.process_html_spaces(text)

  text = read.filters.after_second_comment_line(text)

  verses = read.filters.split_verses_at_br(text)
  verses = read.filters.split_further_at_verse_numbers(verses)

  verses = [verse for verse in verses if
            not read.filters.is_parenthesized_line(verse) and
            not read.filters.is_empty(verse) and
            not read.filters.is_header_line(verse) and
            not read.filters.is_footnote_line(verse) and
            not read.filters.is_asterisked_variant_line(verse) and
            not read.filters.is_footnote_followed_by_parenthesized_line(verse) and
            not read.filters.is_html_footer_line(verse) and
            not read.filters.is_verses_found_elsewhere_line(verse) and
            not read.filters.starts_with_br(verse) and
            not read.filters.is_edition_info(verse) and
            not read.filters.is_abbreviation_block(verse)]

  verses = map(read.filters.clean_leading_br, verses)
  verses = map(read.filters.clean_leading_parenthesized_line, verses)
  verses = map(read.filters.clean_leading_footnote, verses)

  # Print('These are verses:')
  # for (i, verse) in enumerate(verses):
  #   # if not re.match(r'^(.*<BR>\n){3}.*<BR>$', verse) and not re.match(r'^.*<BR>\n.*<BR>$', verse):
  #     Print('\nVerse %d is:' % i)
  #     Print('\n    '.join(('    ' + verse).splitlines()))
  #     Print('End Verse %d\n' % i)


  identifier = identifier_pipeline.IdentifierPipeline()
  table = {}
  for (verse_number, verse) in enumerate(verses):
    ok_and_results = identifier.IdentifyFromText(verse)
    if not ok_and_results:      # None for lines that contain no syllables
      continue
    (perfect, results) = ok_and_results
    if not results:
      table['unknown'] = table.get('unknown', 0) + 1
      if args.print_unidentified_verses != 'none':
        Print('Verse %4d:' % (verse_number + 1))
        if args.print_unidentified_verses == 'full':
          Print(verse)
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
        Print(verse)
    table[metre_name] = table.get(metre_name, 0) + 1
    if not perfect and args.break_at_error:
      Print(verse)
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
