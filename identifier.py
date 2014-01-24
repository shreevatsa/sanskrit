#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Module to identify metre from scanned verse.

Usage from Python code:
     import identifier
     verse_lines = ['line 1 of verse', 'line 2 of verse', ...]
     identifier = identifier.Identifier()
     identifier.IdentifyFromLines(verse)
     # also look at identifier.AllDebugOutput()
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re

import match_result


class Identifier(object):
  """An object used to make a single metre-identification call."""

  def __init__(self, metrical_data):
    self.output = []
    self.metrical_data = metrical_data
    logging.info('Identifier is initialized. It knows %d metre regexes,'
                 ' %d metre patterns, %d partial regexes, and'
                 ' %d partial patterns',
                 len(self.metrical_data.known_metre_regexes),
                 len(self.metrical_data.known_metre_patterns),
                 len(self.metrical_data.known_partial_regexes),
                 len(self.metrical_data.known_partial_patterns))

  def Reset(self):
    """Clear all parameters, for use again."""
    self.latest_identified_metre = None
    self.output = []

  def IdentifyMetreFromPattern(self, verse):
    """Given metrical pattern of entire verse, identifies metre."""
    # Join lines of verse into full_verse
    for pattern in verse:
      if not re.match('^[LG]*$', pattern):
        self.output.append('%s is not a pattern (must have only L and G)'
                           % pattern)
        return None
    full_verse = ''.join(verse)

    results = []
    result = self.metrical_data.known_metre_patterns.get(full_verse)
    if result:
      return [result]

    for (known_regex, known_metre) in self.metrical_data.known_metre_regexes:
      if known_regex.match(full_verse):
        self.latest_identified_metre = known_metre
        results.append(known_metre)
        return results

    # The pattern was not recognized; look at mātrās.
    morae = [MatraCount(line) for line in verse]

    assert not results
    # Nothing recognized, need to examine lines individually
    self.output.append(
        'Metre unknown. There are %d (%s) syllables (%d mātra units).' %
        (len(full_verse), ' + '.join(unicode(len(line)) for line in verse),
         sum(morae)))

    for (i, line) in enumerate(verse):
      identified = self.IdentifyPattern(line)
      if identified:
        assert isinstance(identified, list), identified
        assert all(isinstance(p, match_result.MatchResult)
                   for p in identified)
        results.extend(identified)
        self.output.append('  Line %d: pattern %s (%d syllables, %d mātras) is '
                           '%s' % (i + 1, line, len(line),
                                   morae[i], match_result.Names(identified)))
      else:
        self.output.append('  Line %d: pattern %s (%d syllables, %d mātras) is '
                           'unknown' % (i + 1, line, len(line), morae[i]))
    return results

  def IdentifyFromLines(self, pattern_lines):
    """Takes a bunch of verse lines as input, and identifies metre."""
    self.Reset()

    results = self.IdentifyMetreFromPattern(pattern_lines)
    if not results:
      return None
    assert isinstance(results, list)
    assert all(isinstance(p, match_result.MatchResult) for p in results)
    if len(results) == 1:
      self.output.append('Identified as %s.' % results[0].Name())
      return results
    # TODO(shreevatsa): Do some merging of the results here
    return results

  def IdentifyPattern(self, pattern):
    """Given metrical pattern (string of L's and G's), identifies metre."""
    assert re.match('^[LG]*$', pattern)
    results = self.metrical_data.known_partial_patterns.get(pattern)
    if results is not None:
      assert isinstance(results, list), (unicode(results), type(results))
      for result in results:
        assert isinstance(result, match_result.MatchResult), result
    else:
      assert results is None
      for (known_regex,
           known_result) in self.metrical_data.known_partial_regexes:
        if known_regex.match(pattern):
          results = [known_result]
          break
    return results


def MatraCount(pattern):
  assert re.match('^[LG]*$', pattern)
  return sum(2 if c == 'G' else 1 for c in pattern)
