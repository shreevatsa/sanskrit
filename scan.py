"""Given lines in SLP1, converts them to patterns of laghus and gurus."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import slp1

_SYLLABLE_RE = slp1.VOWEL_RE + slp1.CONSONANT_RE + '*'


def ScanVerse(lines):
  cleaned_lines = _MoveInitialConsonants(lines)
  return [_Scan(line) for line in cleaned_lines]


def _MoveInitialConsonants(verse_lines):
  """Move initial consonants of each line to the end of the previous line."""
  for i in xrange(1, len(verse_lines)):
    (consonants, verse_lines[i]) = _StripInitialConsonants(verse_lines[i])
    verse_lines[i - 1] += consonants
  return verse_lines


def _StripInitialConsonants(text):
  m = re.match(slp1.CONSONANT_RE + '+', text)
  initial = m.group() if m else ''
  return (initial, text[len(initial):])


def _Weight(syllable):
  """Whether a syllable (vowel + sequence of consonants) is laghu or guru."""
  assert re.match('^%s$' % _SYLLABLE_RE, syllable)
  if re.search(slp1.LONG_VOWEL_RE, syllable): return 'G'
  if re.search(slp1.CONSONANT_RE + '{2,}', syllable): return 'G'
  return 'L'


def _Scan(text):
  # Even after moving consonants, leading consonants are present in first line.
  (_, text) = _StripInitialConsonants(text)
  syllables = re.findall(_SYLLABLE_RE, text)
  assert text == ''.join(syllables)
  return ''.join(_Weight(s) for s in syllables)
