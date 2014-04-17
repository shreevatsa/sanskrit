# -*- coding: utf-8 -*-
"""Module to identify metre(s) from scanned verse.

The input is a list of "pattern" lines, where a "pattern" is a sequence over the
alphabet {'L', 'G'}. The output is a list of `MatchResult`s.
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
    self._Reset()
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
    self.global_info = []
    self.lines_info = []
    self.halves_info = []
    self.quarters_info = []

  def IdentifyFromLines(self, pattern_lines):
    """Main function. Takes patterns of verse lines and identifies metres."""
    self._Reset()

    full_verse = ''.join(pattern_lines)
    assert _IsPattern(full_verse)
    (global_results, self.global_info) = self._MetresAndInfo(full_verse,
                                                             try_partial=False)
    self.global_info = [self.global_info]

    lines_results = []
    for (i, line) in enumerate(pattern_lines):
      (results, info) = self._MetresAndInfo(line)
      self.lines_info.append('  Line %d: %s' % (i + 1, info))
      lines_results = _MergeResults([lines_results, results])

    if global_results:
      return global_results

    halves_results = []
    quarters_results = []
    for (ab, cd) in _SplitHalves(full_verse):
      (ab_results, ab_info) = self._MetresAndInfo(ab)
      (cd_results, cd_info) = self._MetresAndInfo(cd)
      self.halves_info.append('  Half 1: %s' % ab_info)
      self.halves_info.append('  Half 2: %s' % cd_info)
      halves_results = _MergeResults([halves_results, ab_results, cd_results])
    for quarters in _SplitQuarters(full_verse):
      all_results = []
      for (i, quarter_i) in enumerate(quarters):
        (results, info) = self._MetresAndInfo(quarter_i)
        self.quarters_info.append('  Quarter %d: %s' % (i + 1, info))
        all_results.extend(results)
      quarters_results = _MergeResults([quarters_results, all_results])
    return _MergeResults([global_results, lines_results,
                          halves_results, quarters_results])

  def _MetresAndInfo(self, pattern, try_partial=True):
    assert _IsPattern(pattern)
    results = self._IdentifyPattern(pattern, try_partial)
    name = match_result.Names(results) if results else 'unknown'
    info = ('pattern %s (%d syllables, %d mātras) is %s' %
            (pattern, len(pattern), _MatraCount(pattern), name))
    return (results, info)

  def _IdentifyPattern(self, pattern, try_partial=True):
    """Given metrical pattern (string of L's and G's), identifies metre."""
    full_results = self._IdentifyPatternFrom(
        pattern, self.metrical_data.known_metre_patterns,
        self.metrical_data.known_metre_regexes)
    partial_results = []
    if try_partial:
      partial_results = self._IdentifyPatternFrom(
          pattern,
          self.metrical_data.known_partial_patterns,
          self.metrical_data.known_partial_regexes)
    return _MergeResults([full_results, partial_results])

  def _IdentifyPatternFrom(self, pattern, known_patterns, known_regexes):
    """Identify pattern from given data."""
    results = known_patterns.get(pattern)
    if results:
      if isinstance(results, match_result.MatchResult):
        return [results]
      else:
        return results
    for (known_regex, known_result) in known_regexes:
      if known_regex.match(pattern):
        return [known_result]
    return []


def _MatraCount(pattern):
  return sum(2 if c == 'G' else 1 for c in pattern)


def _MergeResults(results_lists):
  """Return all possible results."""
  # print('Merging %s' % results_lists)
  nonempty_results = []
  for results_list in results_lists:
    assert isinstance(results_list, list)
    for result in results_list:
      assert isinstance(result, match_result.MatchResult), result
      nonempty_results.append(result)
  if len(nonempty_results) == 1:
    return nonempty_results

  # TODO(shreevatsa): Do some uniq of the results here
  return nonempty_results


def _SplitHalves(full_pattern):
  """Attempt splits at halves."""
  splits = []
  n = len(full_pattern)
  if n % 2 == 0:
    m = n // 2
    splits.append([full_pattern[:m], full_pattern[m:]])
  else:
    for m in [(n-1)//2, (n+1)//2]:
      splits.append([full_pattern[:m], full_pattern[m:]])
  return splits


def _SplitQuarters(full_pattern):
  """Attempt splits at quarters."""
  splits = []
  n = len(full_pattern)
  mss = []

  def Cumulative(ns):
    s = 0
    out = []
    for n in ns:
      out.append(n + s)
      s += n
    return out

  if n % 4 == 0:
    m = n // 4
    mss.append(Cumulative([m, m, m]))
  elif n % 4 == 1:
    # The extra syllable could be in any of the four _pāda_s
    m = (n - 1) // 4
    mss.append(Cumulative([m + 1, m, m]))
    mss.append(Cumulative([m, m + 1, m]))
    mss.append(Cumulative([m, m, m + 1]))
    mss.append(Cumulative([m, m, m]))
  elif n % 4 == 2:
    # Either we have two extra syllables...
    m = (n - 2) // 4
    mss.append(Cumulative([m + 1, m + 1, m]))
    mss.append(Cumulative([m + 1, m, m + 1]))
    mss.append(Cumulative([m + 1, m, m]))
    mss.append(Cumulative([m, m + 1, m + 1]))
    mss.append(Cumulative([m, m + 1, m]))
    mss.append(Cumulative([m, m, m + 1]))
    # ... or we're missing two
    m = (n + 2) // 4
    mss.append(Cumulative([m - 1, m - 1, m]))
    mss.append(Cumulative([m - 1, m, m - 1]))
    mss.append(Cumulative([m - 1, m, m]))
    mss.append(Cumulative([m, m - 1, m - 1]))
    mss.append(Cumulative([m, m - 1, m]))
    mss.append(Cumulative([m, m, m - 1]))
  else:
    assert n % 4 == 3
    m = (n + 1) // 4
    # The missing syllable could be in any of the four _pāda_s
    mss.append(Cumulative([m - 1, m, m]))
    mss.append(Cumulative([m, m - 1, m]))
    mss.append(Cumulative([m, m, m - 1]))
    mss.append(Cumulative([m, m, m]))
  for ms in mss:
    splits.append([full_pattern[:ms[0]],
                   full_pattern[ms[0]:ms[1]],
                   full_pattern[ms[1]:ms[2]],
                   full_pattern[ms[2]:]])
  return splits


def _IsPattern(pattern):
  return re.match('^[LG]*$', pattern)
