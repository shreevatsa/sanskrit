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
     See https://github.com/shreevatsa/sanskrit/issues?state=open
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re
import sys

import handle_input
import match_result
import metrical_data
import print_utils
import slp1


class Identifier(object):
  """An object used to make a single metre-identification call."""

  def __init__(self):
    self.output = []
    if not metrical_data.known_patterns:
      metrical_data.InitializeData()
    logging.info('Identifier is initialized. There are %d known metres'
                 ' and %d known_patterns',
                 len(metrical_data.known_metre_regexes),
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
    for (known_regex, known_metre) in metrical_data.known_metre_regexes:
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
      identified = IdentifyPattern(line)
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
    assert all(isinstance(p, match_result.MatchResult) for p in results)
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
    assert isinstance(result, match_result.MatchResult), result
  return results


def Syllabize(text):
  """Given SLP1 text, returns a list of syllables."""
  syllables = re.findall('.*?%s[MH]?' % slp1.ANY_VOWEL, text)

  # Handle final consonants (edge case)
  tail = re.search('(%s+$)' % slp1.CONSONANT, text)
  if syllables and tail:
    match = tail.group(1)
    if match[0] not in 'MH':
      syllables[-1] += tail.group(1)

  return syllables


def MatraCount(pattern):
  assert re.match('^[LG]*$', pattern)
  return sum(2 if c == 'G' else 1 for c in pattern)


def Print(u):
  return print_utils.Print(u)


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.WARNING)
  lines = [l.decode('utf8') for l in sys.stdin]
  identifier = Identifier()
  identifier.IdentifyFromLines(lines)
  Print(identifier.AllDebugOutput())
