"""Given lines in SLP1, converts them to patterns of laghus and gurus."""

from __future__ import absolute_import, division, print_function, unicode_literals
try: xrange
except NameError: xrange = range

import re
import slp1

_SYLLABLE_RE = slp1.VOWEL_RE + slp1.CONSONANT_RE + '*'


def ScanVerse(lines):
  cleaned_lines = _MoveInitialConsonants(lines)
  return [_ScanVowelInitialLine(cleaned_lines[i], i == len(cleaned_lines) - 1)
          for i in range(len(cleaned_lines))]


def _MoveInitialConsonants(verse_lines):
  """Move initial consonants of each line to the end of the previous line."""
  for i in xrange(len(verse_lines)):
    (consonants, verse_lines[i]) = _StripInitialConsonants(verse_lines[i])
    if i > 0 and verse_lines[i - 1]:
      verse_lines[i - 1] += consonants
  return verse_lines


def _StripInitialConsonants(text):
  m = re.match(slp1.CONSONANT_RE + '+', text)
  initial = m.group() if m else ''
  return (initial, text[len(initial):])


def _Weight(syllable, is_final_syllable_of_line=False):
  """Whether a syllable (vowel + sequence of consonants) is laghu or guru."""
  assert re.match('^%s$' % _SYLLABLE_RE, syllable), syllable
  if re.search(slp1.LONG_VOWEL_RE, syllable): return 'G'
  if re.search(slp1.CONSONANT_RE + '{2,}', syllable): return 'G'
  if is_final_syllable_of_line and re.search(slp1.CONSONANT_RE, syllable):
    return 'G'
  return 'L'


def _ScanVowelInitialLine(text, is_last_line=False):
  syllables = re.findall(_SYLLABLE_RE, text)
  assert text == ''.join(syllables), text
  if len(syllables) == 0: return ''
  return (''.join(_Weight(s) for s in syllables[:-1]) +
          _Weight(syllables[-1], is_final_syllable_of_line=is_last_line))
