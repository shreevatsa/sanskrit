#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Print the metrical pattern of given text.

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
import simple_utils


def MetricalPattern(text):
  """Given text in HK, return its metrical pattern (string of 'L's and 'G's)."""
  # A regular-expression "character class" for each type
  consonant = '[MHkgGcjJTDNtdnpbmyrlvzSsh]'
  short_vowel = '[aiuR]'
  long_vowel = '[AIUeo]'
  # vowel = short_vowel.strip(']') + long_vowel.strip('[')
  # Consonants at beginning of text can be ignored
  text = re.sub('^' + consonant + '+', '', text)
  # A long vowel followed by any number of consonants is a guru
  text = re.sub(long_vowel + consonant + '*', '+', text)
  # A short vowel followed by multiple (>=2) consonants is a guru
  text = re.sub(short_vowel + consonant + '{2,}', '+', text)
  # If the line ends in a consonant, the last syllable is a guru
  # TODO(shreevatsa): This requires refinement
  text = re.sub(short_vowel + consonant + '$', '+', text)
  # Any short vowel still left is a laghu; remove it and following consonant
  text = re.sub(short_vowel + consonant + '*', '-', text)
  assert re.match('^[+-]*$', text)
  text = text.replace('-', 'L')
  text = text.replace('+', 'G')
  assert re.match('^[LG]*$', text)
  return text


def IdentitfyPattern(pattern):
  """Given metrical pattern (string of L's and G's), identify metre."""
  if not re.match('^[LG]*$', pattern):
    print '%s is not a pattern (must have only L and G)' % pattern
  return metrical_data.known_patterns.get(pattern, 'unknown')


def IdentifyMetre(verse):
  """Give metrical pattern of entire verse, identify metre."""
  full_verse = ''.join(verse)
  print 'There are %d syllables in the input, in pattern %s.' % (
      len(full_verse), full_verse)

  for known_pattern, known_metre in metrical_data.known_metres.iteritems():
    if re.match('^' + known_pattern + '$', full_verse):
      # print 'Identified as %s, which has pattern:\n    "%s"' % (known_metre,
      #                                                           known_pattern)
      print 'Identified as %s.' % known_metre
      return known_metre

  print 'Metre unknown, trying by lines: '
  for i in range(len(verse)):
    line_i = verse[i]
    print '  Line %d: pattern %s is %s' % (i, line_i, IdentitfyPattern(line_i))


def IdentifyFromLines(input_lines):
  """Take a bunch of verse lines (in HK) as input, and identify metre."""
  pattern_lines = []
  for line in input_lines:
    line = line.strip()
    if not line: continue
    line = handle_input.MassageHK(line)
    # Remove spaces, digits, avagraha, punctuation
    line = simple_utils.RemoveChars(line, " 0123456789'./$&%{}|")
    line = handle_input.CleanHK(line)
    pattern_lines.append(MetricalPattern(line))
  return IdentifyMetre(pattern_lines)


def InitializeData():
  if not metrical_data.known_metres:
    metrical_data.InitializeData()


if __name__ == '__main__':
  InitializeData()
  lines = sys.stdin.readlines()
  IdentifyFromLines(lines)
