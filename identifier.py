# -*- coding: utf-8 -*-
"""Module to identify metre(s) from scanned verse.

The input is a list of "pattern" lines, where a "pattern" is a sequence over the
alphabet {'L', 'G'}. The output is a list of metre names (strings).
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import collections
import logging
import re

import match_result


class Identifier(object):
  """An object used to make a single metre-identification call."""

  def __init__(self, metrical_data):
    self._Reset()
    self.metrical_data = metrical_data
    logging.info('Identifier is initialized. It knows %d metre regexes, %d metre patterns, and %d pada patterns',
                 len(self.metrical_data.known_metre_regexes),
                 len(self.metrical_data.known_metre_patterns),
                 len(self.metrical_data.known_pada_patterns))

  def _Reset(self):
    """Clear all parameters, for use again."""
    self.global_info = []
    self.lines_info = []
    self.halves_info = []
    self.quarters_info = []

  def Identify(self, pattern_lines, input_type):
    parts = _Parts(pattern_lines)
    ret = set()
    for (part, match_with) in _Strategies(input_type):
      # e.g. strategies contains ('full', ('known_metre_patterns', 'known_metre_regexes'))
      ret = ret.union(self._Lookup(parts.get(part), match_with))

  # def IdentifyFromPatternLines(self, pattern_lines):
  #   """Main function. Takes patterns of verse lines and identifies metres."""
  #   self._Reset()

  #   # Too many lines => probably multiple verses.
  #   if len(pattern_lines) > 12:
  #     self.global_info.append('Error: too many lines in verse. '
  #                             'Perhaps these are multiple verses?')
  #     return (False, [])

  #   full_verse = ''.join(pattern_lines)
  #   if not _IsPattern(full_verse): return (False, [])
  #   (global_results, self.global_info) = self._MetresAndInfo(full_verse, try_partial=False)
  #   self.global_info = [self.global_info]

  #   lines_results = []
  #   for (i, line) in enumerate(pattern_lines):
  #     (results, info) = self._MetresAndInfo(line)
  #     self.lines_info.append('  Line %d: %s' % (i + 1, info))
  #     lines_results = _MergeResults([lines_results, results])

  #   if global_results:
  #     return (True, _MergeResults([global_results]))

  #   halves_results = []
  #   quarters_results = []
  #   for (ab, cd) in _SplitHalves(full_verse):
  #     (ab_results, ab_info) = self._MetresAndInfo(ab)
  #     (cd_results, cd_info) = self._MetresAndInfo(cd)
  #     self.halves_info.append('  Half 1: %s' % ab_info)
  #     self.halves_info.append('  Half 2: %s' % cd_info)
  #     halves_results = _MergeResults([halves_results, ab_results, cd_results])
  #   for quarters in _SplitQuarters(full_verse):
  #     all_results = []
  #     for (i, quarter_i) in enumerate(quarters):
  #       (results, info) = self._MetresAndInfo(quarter_i)
  #       self.quarters_info.append('  Quarter %d: %s' % (i + 1, info))
  #       all_results.extend(results)
  #     quarters_results = _MergeResults([quarters_results, all_results])
  #   return (False, _MergeResults([global_results, lines_results,
  #                                 halves_results, quarters_results]))

  # def _MetresAndInfo(self, pattern, try_partial=True):
  #   assert _IsPattern(pattern)
  #   results = self._IdentifyPattern(pattern, try_partial)
  #   name = match_result.Names(results) if results else 'unknown'
  #   info = ('pattern %s (%d syllables, %d mātras) is %s' %
  #           (pattern, len(pattern), _MatraCount(pattern), name))
  #   return (results, info)

  # def _IdentifyPattern(self, pattern, try_partial=True):
  #   """Given metrical pattern (string of L's and G's), identifies metre."""
  #   full_results = _IdentifyPatternFrom(pattern, self.metrical_data.known_metre_patterns, self.metrical_data.known_metre_regexes)
  #   partial_results = []
  #   if try_partial:
  #     partial_results.extend(_IdentifyPatternFrom(pattern, self.metrical_data.known_half_patterns, self.metrical_data.known_half_regexes))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, self.metrical_data.known_first_half_patterns, []))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, self.metrical_data.known_second_half_patterns, []))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, {}, self.metrical_data.known_odd_pada_regexes))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, {}, self.metrical_data.known_even_pada_regexes))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, {}, self.metrical_data.known_pada_regexes))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, self.metrical_data.known_pada_patterns, []))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, self.metrical_data.known_odd_pada_patterns, []))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, self.metrical_data.known_even_pada_patterns, []))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, self.metrical_data.known_pada_1_patterns, []))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, self.metrical_data.known_pada_2_patterns, []))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, self.metrical_data.known_pada_3_patterns, []))
  #     partial_results.extend(_IdentifyPatternFrom(pattern, self.metrical_data.known_pada_4_patterns, []))
  #   ret = full_results + partial_results
  #   return ret

# def _IdentifyPatternFrom(pattern, known_patterns, known_regexes):
#   """Identify pattern from given data."""
#   results = known_patterns.get(pattern)
#   if results:
#     return results
#   # Stop at the first match so that e.g. 'Āryā (strict schema)' hides 'Āryā (loose schema)'
#   for (regex, metre_name) in known_regexes:
#     if regex.match(pattern):
#       return [metre_name]
#   return []


# def _MatraCount(pattern):
#   return sum(2 if c == 'G' else 1 for c in pattern)


# def _MergeResults(results_lists):
#   """Returns a list of metre names without duplicates."""
#   def _UniqList(expr):
#     return list(collections.OrderedDict.fromkeys(expr))
#   names = []
#   for results_list in results_lists:
#     for result in results_list:
#       names.append(result)
#   return _UniqList(names)


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
  def Cumulative(ns):
    """Prefix sums. Example: [5, 4, 3] -> [5, 9, 12]."""
    # return [sum(ns[:i+1]) for i in range(len(ns))]
    s = 0
    out = []
    for n in ns:
      s += n
      out.append(s)
    return out

  splits = []
  mss = []
  n = len(full_pattern)
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
  return re.match('^[LG]+$', pattern)


# TODO(shreevatsa): Distinguish between exact (unique) and approximate halves/padas.
def _Parts(pattern_lines):
  """ {
    'full': [...],
    'half_1': [...],
    'half_2': [...],
    'pada_1': [...],
    'pada_2': [...],
    'pada_3': [...],
    'pada_4': [...],
    'lines': [...] (can overlap with pada_n / half_n)
  }
  """
  pattern_lines = [line for line in pattern_lines if _IsPattern(line)]
  full_pattern = ''.join(pattern_lines)
  ret = {}
  def add(x, e): ret.setdefault(x, set()).add(e)
  ret['full'] = [full_pattern]
  for (ab, cd) in _SplitHalves(full_pattern):
    add('half_1', ab)
    add('half_2', cd)
  for (a, b, c, d) in _SplitQuarters(full_pattern):
    add('pada_1', a)
    add('pada_2', b)
    add('pada_3', c)
    add('pada_4', d)
  ret['lines'] = pattern_lines
  n = len(pattern_lines)
  if n % 2 == 0:
    half_1 = ''.join(pattern_lines[ : n/2])
    add('half_1', half_1)
    for (a, b) in _SplitHalves(half_1):
      add('pada_1', a)
      add('pada_2', b)
    half_2 = ''.join(pattern_lines[n/2 : ])
    add('half_2', half_2)
    for (c, d) in _SplitHalves(half_2):
      add('pada_3', c)
      add('pada_4', d)
  if n % 4 == 0:
    add('pada_1', ''.join(pattern_lines[: n/4]))
    add('pada_2', ''.join(pattern_lines[n/4 : n/2]))
    add('pada_3', ''.join(pattern_lines[n/2 : 3*n/4]))
    add('pada_4', ''.join(pattern_lines[3*n/4 : ]))

def _Strategies(input_type):
  left = ['full',
          'half_1',
          'half_2',
          'pada_1',
          'pada_2',
          'pada_3',
          'pada_4',
          'lines']
  right = ['known_metre_patterns',
           'known_metre_regexes',
           'known_half_patterns',
           'known_half_regexes',
           'known_first_half_patterns',
           'known_second_half_patterns',
           'known_pada_patterns',
           'known_pada_regexes',
           'known_odd_pada_patterns',
           'known_odd_pada_regexes',
           'known_even_pada_patterns',
           'known_even_pada_regexes',
           'known_pada_1_patterns',
           'known_pada_2_patterns',
           'known_pada_3_patterns',
           'known_pada_4_patterns']
  if input_type == 'full':
    return [('full', 'known_metre_patterns'),
            ('full', 'known_metre_regexes'),

            ('half_1', 'known_half_patterns'),
            ('half_1', 'known_half_regexes'),
            ('half_1', 'known_first_half_patterns'),

            ('half_2', 'known_half_patterns'),
            ('half_2', 'known_half_regexes'),
            ('half_2', 'known_second_half_patterns'),

            ('pada_1', 'known_pada_patterns'),
            ('pada_1', 'known_pada_regexes'),
            ('pada_1', 'known_odd_pada_patterns'),
            ('pada_1', 'known_odd_pada_regexes'),
            ('pada_1', 'known_pada_1_patterns'),

            ('pada_2', 'known_pada_patterns'),
            ('pada_2', 'known_pada_regexes'),
            ('pada_2', 'known_even_pada_patterns'),
            ('pada_2', 'known_even_pada_regexes'),
            ('pada_2', 'known_pada_2_patterns'),

            ('pada_3', 'known_pada_patterns'),
            ('pada_3', 'known_pada_regexes'),
            ('pada_3', 'known_odd_pada_patterns'),
            ('pada_3', 'known_odd_pada_regexes'),
            ('pada_3', 'known_pada_3_patterns'),

            ('pada_4', 'known_pada_patterns'),
            ('pada_4', 'known_pada_regexes'),
            ('pada_4', 'known_even_pada_patterns'),
            ('pada_4', 'known_even_pada_regexes'),
            ('pada_4', 'known_pada_4_patterns')]
  if input_type == 'half':
    return [('full', 'known_half_patterns'),
            ('full', 'known_half_regexes'),
            ('full', 'known_first_half_patterns'),
            ('full', 'known_second_half_patterns'),

            ('half_1', 'known_pada_patterns'),
            ('half_1', 'known_pada_regexes'),
            ('half_1', 'known_odd_pada_patterns'),
            ('half_1', 'known_odd_pada_regexes'),
            ('half_1', 'known_pada_1_patterns'),
            ('half_1', 'known_pada_3_patterns'),

            ('half_2', 'known_pada_patterns'),
            ('half_2', 'known_pada_regexes'),
            ('half_2', 'known_even_pada_patterns'),
            ('half_2', 'known_even_pada_regexes'),
            ('half_2', 'known_pada_2_patterns'),
            ('half_2', 'known_pada_4_patterns')]
