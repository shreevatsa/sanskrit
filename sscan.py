#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Prints the metrical pattern of given text.

Usage from commandline:
     python sscan.py
     [input verse]
     Ctrl-D

     or

     python sscan.py < input_file

Usage from Python code:
     import sscan
     verse_lines = ['line 1 of verse', 'line 2 of verse', ...]
     identifier = sscan.Identifier()
     identifier.IdentifyFromLines(verse)
     # also look at identifier.AllDebugOutput()

Known issues:
     (2) Needs a lot more data (metres).
     (3) Missing in output: description of metres.
     (4) When analyzing line-by-line, would be nice to show all resolutions.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re
import sys

import handle_input
import metrical_data
import slp1


class Identifier(object):
  """An object used to make a single metre-identification call."""

  def __init__(self):
    self.output = []
    if not metrical_data.known_metres:
      metrical_data.InitializeData()
    logging.info('Identifier is initialized. There are %d known_metres'
                 ' and %d known_patterns', len(metrical_data.known_metres),
                 len(metrical_data.known_patterns))

  def Reset(self):
    """Clear all parameters, for use again."""
    self.latest_identified_metre = None
    self.output = []
    self.cleaned_output = None

  def AllDebugOutput(self):
    return '\n'.join(self.output)

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
    for (known_pattern, known_metre) in metrical_data.known_metres.iteritems():
      if re.match('^' + known_pattern + '$', full_verse):
        self.latest_identified_metre = known_metre
        results.append(known_metre)
        return results

    # The pattern was not recognized; try mātrā.
    morae = [MatraCount(line) for line in verse]
    if repr(morae) in metrical_data.known_morae:
      known_metre = metrical_data.known_morae[repr(morae)]
      self.latest_identified_metre = known_metre
      results.append(known_metre)
      return results

    assert not results
    # Nothing recognized, need to examine lines individually
    self.output.append(
        'Metre unknown. There are %d (%s) syllables (%d mātra units).' %
        (len(full_verse), ' + '.join(str(len(line)) for line in verse),
         sum(morae)))

    for (i, line) in enumerate(verse):
      identified = IdentifyPattern(line)
      if identified:
        assert isinstance(identified, list), identified
        assert all(isinstance(p, metrical_data.MetrePattern)
                   for p in identified)
        results.extend(identified)
        self.output.append('  Line %d: pattern %s (%d) is %s' % (
            i + 1, line, morae[i], metrical_data.Names(identified)))
      else:
        self.output.append('  Line %d: pattern %s (%d) is unknown' % (
            i + 1, line, morae[i]))
    return results

  def IdentifyFromLines(self, input_lines):
    """Takes a bunch of verse lines as input, and identifies metre."""
    self.Reset()
    logging.info('Got input:\n%s', '\n'.join(input_lines))
    cleaner = handle_input.InputHandler()
    cleaned_lines = cleaner.CleanLines(input_lines)
    self.output.extend(cleaner.error_output)
    self.cleaned_output = cleaner.clean_output
    cleaned_lines = MoveConsonants(cleaned_lines)
    if not cleaned_lines:
      return None

    pattern_lines = []
    for line in cleaned_lines:
      line = MetricalPattern(line)
      pattern_lines.append(line)
    results = self.IdentifyMetreFromPattern(pattern_lines)
    if not results:
      self.output.extend(cleaner.clean_output)
      return None
    assert isinstance(results, list)
    assert all(isinstance(p, metrical_data.MetrePattern) for p in results)
    if len(results) == 1:
      self.output.append('Identified as %s.' % results[0].Name())
      return results
    # TODO(shreevatsa): Do some merging of the results here
    return results


def MoveConsonants(verse_lines):
  consonant = slp1.CONSONANT
  for i in xrange(1, len(verse_lines)):
    text = verse_lines[i]
    m = re.match(consonant + '+', text)
    if m:
      verse_lines[i - 1] += m.group()
      verse_lines[i] = verse_lines[i][len(m.group()):]
  return verse_lines


def MetricalPattern(text):
  """Given SLP1 text, returns its metrical pattern (string of 'L's and 'G's)."""
  orig_text = text
  # A regular-expression "character class" for each type
  consonant = slp1.CONSONANT
  short_vowel = slp1.SHORT_VOWEL
  long_vowel = slp1.LONG_VOWEL
  # Consonants at beginning of text can be ignored
  text = re.sub('^' + consonant + '+', '', text)
  # A long vowel followed by any number of consonants is a guru
  text = re.sub(long_vowel + consonant + '*', '+', text)
  # A short vowel followed by multiple (>=2) consonants is a guru
  text = re.sub(short_vowel + consonant + '{2,}', '+', text)
  # # TODO(shreevatsa): Should short_vowel + visarga be special-cased to guru?
  # text = re.sub(short_vowel + 'H$', '+', text)
  # Any short vowel still left is a laghu; remove it and following consonant
  text = re.sub(short_vowel + consonant + '?', '-', text)
  assert re.match('^[+-]*$', text), (orig_text, text)
  text = text.replace('-', 'L')
  text = text.replace('+', 'G')
  assert re.match('^[LG]*$', text)
  return text


def IdentifyPattern(pattern):
  """Given metrical pattern (string of L's and G's), identifies metre."""
  assert re.match('^[LG]*$', pattern)
  results = metrical_data.known_patterns.get(pattern)
  if results is None:
    return results
  assert isinstance(results, list), results
  for result in results:
    assert isinstance(result, metrical_data.MetrePattern), result
  return results


def MatraCount(pattern):
  assert re.match('^[LG]*$', pattern)
  return sum(2 if c == 'G' else 1 for c in pattern)


def Print(u):
  assert isinstance(u, unicode)
  print(u.encode('utf8'))


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.WARNING)
  lines = [l.decode('utf8') for l in sys.stdin]
  identifier = Identifier()
  identifier.IdentifyFromLines(lines)
  Print(identifier.AllDebugOutput())
