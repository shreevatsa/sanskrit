#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Reads from a GRETIL UTF-8 encoded HTML file."""

from __future__ import absolute_import, division, print_function, unicode_literals
try: unicode
except NameError: unicode = str

import argparse
import codecs
import json
import logging
import os.path
import tempfile

# from IPython.core.debugger import Tracer
# assert Tracer  # to slience Pyflakes

from print_utils import Print
import read.split_gretil
import read
import scan
import identifier_pipeline
from data import metrical_data
import display


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


# A function that can be used (pure).
# text: an entire file (see caller)
# args: see caller
# custom_splitter: can usually be None (see caller)
# Returns a dict called 'ret':
#   num_verses: <int>
#   verses: {
#      verse_number: <int>
#      messages: [...]
#      result: {metre_name: metre_name, is_perfect: is_perfect}
#      messages2: [...]
#   }
#   table: {
#      unknown: <int>
#      Anuṣṭup (Śloka): <int>
#      ...
#   }
#   sum_counts: <int> (ideally, should be same as num_verses)
def metres_for_text(text, args, custom_splitter):
  (verses, text) = read.split_gretil.split(text, custom_splitter=custom_splitter)
  # blocks = list(read.split_gretil.blocks_of_verses_in_text(verses, text))
  ret = {}
  ret['num_verses'] = len(verses)
  ret['verses'] = {}

  identifier = identifier_pipeline.IdentifierPipeline()
  table = {}
  for (verse_number, verse) in enumerate(verses):
    verse_number += 1
    # Print('\nVerse %d is:' % verse_number)
    # Print('\n    '.join(('    ' + verse).splitlines()))
    # Print('End Verse %d' % verse_number)
    ok_and_results = identifier.IdentifyFromText(verse)
    if not ok_and_results:      # None for lines that contain no syllables
      continue
    (perfect, results) = ok_and_results
    ret['verses'][verse_number] = {}
    cur = ret['verses'][verse_number]
    cur['verse'] = verse
    cur['messages'] = []
    cur['messages2'] = []
    cur['result'] = {}

    if not results:
      table['unknown'] = table.get('unknown', 0) + 1
      if args['print_unidentified_verses'] != 'none':
        cur['messages'].append('Verse %4d:' % verse_number)
        if args['print_unidentified_verses'] == 'full':
          cur['messages'].append(verse)
          cur['messages'].append(identifier.AllDebugOutput())
          cur['messages'].append('')
      continue

    # We've dealt with the case where there are no results
    assert results
    assert isinstance(results, list)
    metre_name = results[0]
    if args['print_identified_verses'] != 'none':
      cur['result'] = {
        'metre_name': metre_name,
        'is_perfect': perfect,
      }
      if args['print_identified_verses'] == 'full':
        cur['messages2'].append(verse)
    table[metre_name] = table.get(metre_name, 0) + 1
    if not perfect and args['break_at_error']:
      cur['messages2'].append(verse)
      cur['messages2'].append(identifier.AllDebugOutput())
      cur['messages2'].append('')
      break

  sum_counts = sum(value for (key, value) in table.items())
  for (metre, count) in table.items():
    table[metre] = [count, '%.2f%%' % (count * 100 / sum_counts)]
  ret['table'] = table
  ret['sum_counts'] = sum_counts
  return ret

def find_alignment(verse_text, metre_name):
    print(type(verse_text))
    print(type(metre_name))
    Print(['Asked to find alignment for: ', verse_text, ' and ', metre_name])
    (cleaned_lines, display_lines) = read.read.read_text(verse_text)
    pattern_lines = scan.ScanVerse(cleaned_lines)
    if not pattern_lines:
      return None
    # TODO: This is very slow, should reuse.
    # identifier = identifier_pipeline.IdentifierPipeline()
    # results = identifier.IdentifyFromPatternLines(pattern_lines)
    known_pattern = metrical_data.GetPattern(metre_name)
    if known_pattern:
        alignment = display.AlignVerseToMetre(display_lines, ''.join(pattern_lines), known_pattern)
        table = display.HtmlTableFromAlignment(alignment)
        return (alignment, table)
    else:
        return ('', '')

if __name__ == '__main__':
  args = get_args()
  input_file_name = args.input_file
  set_up_logger(input_file_name)

  text = codecs.open(input_file_name, 'r', 'utf-8').read()
  custom_splitter = read.split_gretil.mss_splitter if 'msubhs_u.htm' in input_file_name else None
  args2 = {
    'print_identified_verses': args.print_identified_verses,
    'print_unidentified_verses': args.print_unidentified_verses,
    'break_at_error': args.break_at_error,
  }
  # Split into verses, and return data for each verse. (And global metadata.)
  ret = metres_for_text(text, args2, custom_splitter)
  Print('There are %d verses.' % ret['num_verses'])
  for verse_number in ret['verses']:
    cur = ret['verses'][verse_number]
    Print('Verse number %d' % verse_number)
    for message in cur['messages']:
      Print(message)
    if 'result' in cur:
      metre_name = cur['result']['metre_name']
      perfect = cur['result']['is_perfect']
      Print('Verse %4d is%sin %s' % (
          verse_number,
          ' ' if perfect else ' probably ',
          metre_name))
    for message in cur['messages2']:
      Print(message)

  table = ret['table']
  sum_counts = ret['sum_counts']

  Print(table)
  Print("That's %d verses in all." % sum_counts)

  stats_file_name = os.path.basename(input_file_name) + '.stats'
  stats_file = codecs.open(stats_file_name, 'w', 'utf-8')
  json.dump(table, stats_file, indent=2, ensure_ascii=False,
            separators=(',', ': '))
  stats_file.close()
  stats_file = codecs.open(stats_file_name, 'r', 'utf-8')
  assert table == json.load(stats_file, 'utf-8')


