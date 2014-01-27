"""Unit tests for the syllabize function of sscan."""

import unittest

from scan import Syllables
import slp1

VOWELS = 'aAiIuUfFxXeEoO'


class SyllabizeTest(unittest.TestCase):
  def testEmpty(self):
    """Syllables should return an empty list on empty input."""
    empty = []
    assert Syllables('') == empty

  def testConsonantWithoutVowels(self):
    """Syllables should return an empty list for a consonant without vowels."""
    empty = []
    assert Syllables('k') == empty

  def testConsonantsWithoutVowels(self):
    """Syllables should return an empty list for consonants without vowels."""
    empty = []
    assert Syllables('rtsny') == empty

  def testSingleFinalVowel(self):
    """A single vowel (preceded by a consonant) should syllabize at itself."""
    for v in VOWELS:
      assert Syllables(v) == [(v, 'L' if v in slp1.SHORT_VOWEL else 'G')]
      assert Syllables('kr' + v) == [('kr' + v,
                                      'L' if v in slp1.SHORT_VOWEL else 'G')]

  def testSingleVowelWithConsonant(self):
    """A single vowel, followed by a consonant, should syllabize as itself."""
    for v in VOWELS:
      assert Syllables(v + 'rj') == [(v + 'rj', 'G')]

  def testWords(self):
    def Ok(text, syllables, weights):
      assert Syllables(text) == zip(syllables.split(),
                                    list(weights)), (Syllables(text),
                                                     syllables,
                                                     weights)
    Ok('kA', 'kA', 'G')
    Ok('kAn', 'kAn', 'G')
    Ok('na', 'na', 'L')
    Ok('gamana', 'ga ma na', 'LLL')
    Ok('cARUraH', 'cA RU raH', 'GGG')
    Ok('haMsena', 'haM se na', 'GGL')
    Ok('pradIpasya', 'pra dI pa sya', 'LGGL')
    Ok('kArtsnyam', 'kA rtsnyam', 'GG')


if __name__ == '__main__':
  unittest.main()
