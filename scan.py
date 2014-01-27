"""Given lines in SLP1, converts them to a pattern of laghus and gurus."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import slp1


def _PatternFromLine(text):
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
  old = [_PatternFromLine(line) for line in cleaned_lines]
  new = [''.join(s[1] for s in Syllables(line)) for line in cleaned_lines]
  assert old == new, (old, new, Syllables(line))
  return new


def _StripInitialConsonants(text):
  m = re.match(slp1.CONSONANT + '+', text)
  if m:
    initial = m.group()
  else:
    initial = ''
  return (initial, text[len(initial):])


def Weight(syllable):
  """Whether a syllable is laghu or guru."""
  assert re.match('^%s%s*$' % (slp1.ANY_VOWEL, slp1.CONSONANT), syllable)
  if re.search(slp1.LONG_VOWEL, syllable):
    return 'G'
  if re.search(slp1.CONSONANT + '{2,}', syllable):
    return 'G'
  return 'L'


def _MoveConsonants(verse_lines):
  for i in xrange(1, len(verse_lines)):
    (consonants, verse_lines[i]) = _StripInitialConsonants(verse_lines[i])
    verse_lines[i - 1] += consonants
  return verse_lines


def Syllables(text):
  (initial_consonants, text) = _StripInitialConsonants(text)
  syllables = re.findall(slp1.ANY_VOWEL + slp1.CONSONANT + '*', text)
  syllables = [(s, Weight(s)) for s in syllables]
  if syllables:
    syllables[0] = (initial_consonants + syllables[0][0], syllables[0][1])
  return syllables
