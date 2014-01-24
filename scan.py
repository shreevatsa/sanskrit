#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Given lines in SLP1, converts them to a pattern of laghus and gurus."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import slp1


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


def ScanVerse(lines):
  cleaned_lines = _MoveConsonants(lines)
  if not cleaned_lines:
    return None
  pattern_lines = []
  for line in cleaned_lines:
    line = MetricalPattern(line)
    pattern_lines.append(line)
  return pattern_lines


def _MoveConsonants(verse_lines):
  consonant = slp1.CONSONANT
  for i in xrange(1, len(verse_lines)):
    text = verse_lines[i]
    m = re.match(consonant + '+', text)
    if m:
      verse_lines[i - 1] += m.group()
      verse_lines[i] = verse_lines[i][len(m.group()):]
  return verse_lines


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
