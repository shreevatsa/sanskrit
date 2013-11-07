#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Prints the metrical pattern of given text.

Usage:
     python sscan.py
     [input verse]
     Ctrl-D

     or

     python sscan.py < input_file

Known issues:
     (1) Needs better treatment of pādānta-guru / pādānta-yati.
     (2) Needs a lot more data (metres).
     (3) Missing in output: description of metres.
     (4) When analyzing line-by-line, would be nice to show all resolutions.
"""

from __future__ import unicode_literals
import re
import sys

import handle_input
import metrical_data
import slp1


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


def IdentitfyPattern(pattern):
  """Given metrical pattern (string of L's and G's), identifies metre."""
  if not re.match('^[LG]*$', pattern):
    print '%s is not a pattern (must have only L and G)' % pattern
  return metrical_data.known_patterns.get(pattern, 'unknown')


def IdentifyMetre(verse):
  """Given metrical pattern of entire verse, identifies metre."""
  full_verse = ''.join(verse)
  print 'There are %d (%s) syllables.' % (
      len(full_verse), ' + '.join(str(len(line)) for line in verse))

  for known_pattern, known_metre in metrical_data.known_metres.iteritems():
    if re.match('^' + known_pattern + '$', full_verse):
      print 'Identified as %s.' % known_metre
      return known_metre

  print 'Metre unknown, trying by lines: '
  for i in range(len(verse)):
    line_i = verse[i]
    print '  Line %d: pattern %s is %s' % (i, line_i, IdentitfyPattern(line_i))


def IdentifyFromLines(input_lines):
  """Takes a bunch of verse lines (in HK) as input, and identifies metre."""
  InitializeData()
  input_lines = handle_input.CleanLines(input_lines)
  cleaned_lines = MoveConsonants(input_lines)
  pattern_lines = []
  for i in range(len(cleaned_lines)):
    line = MetricalPattern(cleaned_lines[i])
    if i % 2 and line.endswith('L'):
      print 'Promoting last laghu of line %d to guru' % (i + 1)
      line = line[:-1] + 'G'
    pattern_lines.append(line)
  return IdentifyMetre(pattern_lines)


def InitializeData():
  if not metrical_data.known_metres:
    metrical_data.InitializeData()


if __name__ == '__main__':
  InitializeData()
  lines = []
  for l in sys.stdin:
    l = handle_input.RemoveHTML(l.decode('utf8'))
    (l, n) = handle_input.RemoveVerseNumber(l)
    lines.append(l)
    if n:
      lines.append('')
  IdentifyFromLines(lines)
