# -*- coding: utf-8 -*-
"""Module to identify metre from scanned verse."""

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

  def _Reset(self):
    """Clear all parameters, for use again."""
    self.output = []

  def IdentifyFromLines(self, pattern_lines):
    """Wrapper. Takes patterns of verse lines as input and identifies metres."""
    self._Reset()

    results = self._IdentifyMetresFromPatterns(pattern_lines)
    if not results:
      return None
    _CheckListOfResults(results)
    if len(results) == 1:
      self.output.append('Identified as %s.' % results[0].Name())
      return results
    # TODO(shreevatsa): Do some merging of the results here
    return results

  def _IdentifyMetresFromPatterns(self, verse):
    """Given metrical pattern of each line of verse, identifies metres."""
    full_verse = ''.join(verse)
    assert re.match('^[LG]*$', full_verse)

    morae = [_MatraCount(line) for line in verse]
    self.output.append('The input has %d syllables and %d mātra units.' %
                       (len(full_verse), sum(morae)))

    results = []
    for (i, line) in enumerate(verse):
      line_metre = 'unknown'
      identified = self._IdentifyPattern(line)
      if identified:
        results.extend(_CheckListOfResults(identified))
        line_metre = match_result.Names(identified)
      self.output.append('  Line %d: pattern %s (%d syllables, %d mātras) is %s'
                         % (i + 1, line, len(line), morae[i], line_metre))

    result = self.metrical_data.known_metre_patterns.get(full_verse)
    if result:
      return [result]
    for (known_regex, known_metre) in self.metrical_data.known_metre_regexes:
      if known_regex.match(full_verse):
        return [known_metre]
    # Nothing recognized for full verse, return results of line-by-line.
    return results

  def _IdentifyPattern(self, pattern):
    """Given metrical pattern (string of L's and G's), identifies metre."""
    results = self.metrical_data.known_partial_patterns.get(pattern)
    if results is not None:
      _CheckListOfResults(results)
    else:
      for (known_regex,
           known_result) in self.metrical_data.known_partial_regexes:
        if known_regex.match(pattern):
          results = [known_result]
          break
    return results


def _MatraCount(pattern):
  return sum(2 if c == 'G' else 1 for c in pattern)


def _CheckListOfResults(results):
  assert isinstance(results, list), results
  assert all(isinstance(result, match_result.MatchResult)
             for result in results)
  return results
