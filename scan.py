"""Given lines in SLP1, converts them to patterns of laghus and gurus."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import slp1


def ScanVerse(lines):
  cleaned_lines = _MoveConsonants(lines)
  return [_Scan(line) for line in cleaned_lines]


def _MoveConsonants(verse_lines):
  """Move initial consonants of each line to the end of the previous line."""
  for i in xrange(1, len(verse_lines)):
    (consonants, verse_lines[i]) = _StripInitialConsonants(verse_lines[i])
    verse_lines[i - 1] += consonants
  return verse_lines


def _StripInitialConsonants(text):
  m = re.match(slp1.CONSONANT + '+', text)
  initial = m.group() if m else ''
  return (initial, text[len(initial):])


def _Weight(syllable):
  """Whether a syllable (vowel + sequence of consonants) is laghu or guru."""
  assert re.match('^%s%s*$' % (slp1.ANY_VOWEL, slp1.CONSONANT), syllable)
  if re.search(slp1.LONG_VOWEL, syllable): return 'G'
  if re.search(slp1.CONSONANT + '{2,}', syllable): return 'G'
  return 'L'


def _Scan(text):
  (unused_initial_consonants, text) = _StripInitialConsonants(text)
  syllables = re.findall(slp1.ANY_VOWEL + slp1.CONSONANT + '*', text)
  assert ''.join(syllables) == text
  return ''.join(_Weight(s) for s in syllables)
