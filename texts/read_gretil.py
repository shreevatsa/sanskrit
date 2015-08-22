#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Reads from a GRETIL UTF-8 encoded HTML file."""

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import codecs
import json
import logging
import os.path
import tempfile

from IPython.core.debugger import Tracer
assert Tracer  # to slience Pyflakes

from print_utils import Print
import read.split_gretil
import identifier_pipeline


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
  custom_splitter = read.split_gretil.mss_splitter if 'msubhs_u.htm' in input_file_name else None
  (verses, text) = read.split_gretil.split(text, custom_splitter=custom_splitter)
  # blocks = list(read.split_gretil.blocks_of_verses_in_text(verses, text))
  Print('There are %d verses.' % len(verses))

  identifier = identifier_pipeline.IdentifierPipeline()
  table = {}
  for (verse_number, verse) in enumerate(verses):
    verse_number += 1
    Print('\nVerse %d is:' % verse_number)
    Print('\n    '.join(('    ' + verse).splitlines()))
    Print('End Verse %d' % verse_number)
    ok_and_results = identifier.IdentifyFromText(verse)
    if not ok_and_results:      # None for lines that contain no syllables
      continue
    (perfect, results) = ok_and_results
    if not results:
      table['unknown'] = table.get('unknown', 0) + 1
      if args.print_unidentified_verses != 'none':
        Print('Verse %4d:' % verse_number)
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
          verse_number,
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
