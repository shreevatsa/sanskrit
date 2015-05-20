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
    logging.info('Identifier is initialized. It knows %d full regexes, %d full patterns, %d half regexes, %d half patterns, %d pada regexes, %d pada patterns',
                 len(self.metrical_data.known_full_regexes), len(self.metrical_data.known_full_patterns),
                 len(self.metrical_data.known_half_regexes), len(self.metrical_data.known_half_patterns),
                 len(self.metrical_data.known_pada_regexes), len(self.metrical_data.known_pada_patterns))

  def _Reset(self):
    """Clear all parameters, for use again."""
    self.global_debug = []
    self.parts_debug = []

  @staticmethod
  def MatchesIn(pattern, known_patterns, known_regexes):
    result_matches = known_patterns.get(pattern)
    if result_matches:
      return result_matches
    for (regex, matches) in known_regexes:
      if regex.match(pattern):
        return matches

  def MatchesFor(self, pattern, input_type, part_type, debug_indentation_depth):
    ret = {}
    # 1. Try full matches
    full_matches = self.MatchesIn(pattern, self.metrical_data.known_full_patterns, self.metrical_data.known_full_regexes)
    if full_matches:
      for (metre_name, value) in full_matches.items():
        assert value == True, pattern
        match_type = None
        if input_type == 'full' and part_type == 'full':
          match_type = 'exact'
        else:
          match_type = 'accidental'
        self.parts_debug.append(' %s %s match for: %s %s' % (' ' * debug_indentation_depth, match_type, metre_name, value))
        ret.setdefault(match_type, set()).add(metre_name)
    # 2. Try half matches
    half_matches = self.MatchesIn(pattern, self.metrical_data.known_half_patterns, self.metrical_data.known_half_regexes)
    if half_matches:
      for (metre_name, value) in half_matches.items():
        match_type = None
        if (input_type == 'full' and (part_type == 'half_1' and 1 in value or
                                      part_type == 'half_2' and 2 in value) or
            input_type == 'half' and part_type == 'full'):
          match_type = 'partial'
        else:
          match_type = 'accidental'
        self.parts_debug.append(' %s %s match for: %s %s' % (' ' * debug_indentation_depth, match_type, metre_name, value))
        ret.setdefault(match_type, set()).add(metre_name)
    # 3. Try pada matches
    pada_matches = self.MatchesIn(pattern, self.metrical_data.known_pada_patterns, self.metrical_data.known_pada_regexes)
    if pada_matches:
      for (metre_name, value) in pada_matches.items():
        match_type = None
        if (input_type == 'full' and (part_type == 'pada_1' and 1 in value or
                                      part_type == 'pada_2' and 2 in value or
                                      part_type == 'pada_3' and 3 in value or
                                      part_type == 'pada_4' and 4 in value) or
           (input_type == 'half' and (part_type == 'half_1' and (1 in value or 3 in value) or
                                      part_type == 'half_2' and (2 in value or 4 in value))) or
            input_type == 'pada' and part_type == 'full'):
          match_type = 'partial'
        else:
          match_type = 'accidental'
        self.parts_debug.append(' %s %s match for: %s %s' % (' ' * debug_indentation_depth, match_type, metre_name, value))
        ret.setdefault(match_type, set()).add(metre_name)
    return ret

  @staticmethod
  def union(d, e):
    for key in e:
      d.setdefault(key, set()).update(e[key])
    return d

  def IdentifyFromPatternLines(self, pattern_lines, input_type='full'):
    self._Reset()
    # Too many lines => probably multiple verses.
    if len(pattern_lines) > 12:
      self.global_debug.append('Error: too many lines in verse. Perhaps these are multiple verses?')
      return {}

    ret = {}  # { 'exact': {..}, 'partial': {...}, 'accidental': {..} }

    for (part_type, part_patterns) in _Parts(pattern_lines):
      for pattern in part_patterns:
        self.parts_debug.append('  %s pattern %s (%d syllables, %d mātras)' % (part_type, pattern, len(pattern), _MatraCount(pattern)))
        last_debug_line_length = len(self.parts_debug[-1])
        ret = self.union(ret, self.MatchesFor(pattern, input_type, part_type, last_debug_line_length))
    # Done looping over all part types.
    return ret


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
  }.items() (ordered)
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
  # Add groups of lines to 'half_*' and 'pada_*'
  n = len(pattern_lines)
  if n % 2 == 0:
    half_1 = ''.join(pattern_lines[ : n//2])
    add('half_1', half_1)
    for (a, b) in _SplitHalves(half_1):
      add('pada_1', a)
      add('pada_2', b)
    half_2 = ''.join(pattern_lines[n//2 : ])
    add('half_2', half_2)
    for (c, d) in _SplitHalves(half_2):
      add('pada_3', c)
      add('pada_4', d)
  if n % 4 == 0:
    add('pada_1', ''.join(pattern_lines[: n//4]))
    add('pada_2', ''.join(pattern_lines[n//4 : n//2]))
    add('pada_3', ''.join(pattern_lines[n//2 : 3*n//4]))
    add('pada_4', ''.join(pattern_lines[3*n//4 : ]))
  if n not in [1, 2, 4]:
    # When n is 1, 2, or 4, each line already accounted for as full/half/pada.
    ret['lines'] = pattern_lines
  return [
           ('full', ret.get('full', set())),
           ('half_1', ret.get('half_1', set())),
           ('half_2', ret.get('half_2', set())),
           ('pada_1', ret.get('pada_1', set())),
           ('pada_2', ret.get('pada_2', set())),
           ('pada_3', ret.get('pada_3', set())),
           ('pada_3', ret.get('pada_4', set())),
           ('lines', ret.get('lines', set()))
         ]

def _MatraCount(pattern):
  return sum(2 if c == 'G' else 1 for c in pattern)
