"""Unit tests for the syllabize function of sscan."""

import unittest

from sscan import Syllabize

VOWELS = 'aAiIuUfFxXeEoO'


class SyllabizeTest(unittest.TestCase):
  def testEmpty(self):
    """Syllabize should return an empty list on empty input."""
    empty = []
    assert Syllabize('') == empty

  def testConsonantWithoutVowels(self):
    """Syllabize should return an empty list for a consonant without vowels."""
    empty = []
    assert Syllabize('k') == empty

  def testConsonantsWithoutVowels(self):
    """Syllabize should return an empty list for consonants without vowels."""
    empty = []
    assert Syllabize('rtsny') == empty

  def testSingleFinalVowel(self):
    """A single vowel (preceded by a consonant) should syllabize at itself."""
    for v in VOWELS:
      assert Syllabize(v) == [v]
      assert Syllabize('kr' + v) == ['kr' + v]

  def testSingleVowelWithConsonant(self):
    """A single vowel, followed by a consonant, should syllabize as itself."""
    for v in VOWELS:
      assert Syllabize(v + 'rj') == [v + 'rj']

  def testWords(self):
    def Ok(data, result):
      assert Syllabize(data) == result.split()
      Ok('gamana', 'ga ma na')
      Ok('cARUraH', 'cA RU raH')
      Ok('haMsena', 'haM se na')
      Ok('pradIpasya', 'pra dI pa sya')
      Ok('kArtsnyam', 'kA rtsnyam')


if __name__ == '__main__':
  unittest.main()
