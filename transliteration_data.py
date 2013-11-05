# -*- coding: utf-8 -*-

"""Transliteration data."""

from __future__ import unicode_literals

import devanagari
import slp1
import transliterate


def AlphabetToSLP1(alphabet):
  """Table, given a transliteration convention's alphabet in standard order."""
  return dict(zip(alphabet, slp1.ALPHABET))


HK_ALPHABET = (list('aAiIuUR') + ['RR', 'lR', 'lRR', 'e', 'ai', 'o', 'au'] +
               ['M', 'H',
                'k', 'kh', 'g', 'gh', 'G',
                'c', 'ch', 'j', 'jh', 'J',
                'T', 'Th', 'D', 'Dh', 'N',
                't', 'th', 'd', 'dh', 'n',
                'p', 'ph', 'b', 'bh', 'm'] +
               list('yrlvzSsh'))


def HKToSLP1StateMachine():
  return transliterate.MakeStateMachine(AlphabetToSLP1(HK_ALPHABET))


def IASTToSLP1Table():
  """Transliteration table from IAST to SLP1."""
  lower = AlphabetToSLP1(list('aāiīuūṛṝḷḹe') + ['ai', 'o', 'au', 'ṃ', 'ḥ'] +
                         ['k', 'kh', 'g', 'gh', 'ṅ',
                          'c', 'ch', 'j', 'jh', 'ñ',
                          'ṭ', 'ṭh', 'ḍ', 'ḍh', 'ṇ',
                          't', 'th', 'd', 'dh', 'n',
                          'p', 'ph', 'b', 'bh', 'm',
                          'y', 'r', 'l', 'v', 'ś', 'ṣ', 's', 'h'])
  upper = AlphabetToSLP1(list('AĀIĪUŪṚṜḶḸE') + ['AI', 'O', 'AU', 'Ṃ', 'Ḥ'] +
                         ['K', 'Kh', 'G', 'Gh', 'Ṅ',
                          'C', 'Ch', 'J', 'Jh', 'Ñ',
                          'Ṭ', 'Ṭh', 'Ḍ', 'Ḍh', 'Ṇ',
                          'T', 'Th', 'D', 'Dh', 'N',
                          'P', 'Ph', 'B', 'Bh', 'M',
                          'Y', 'R', 'L', 'V', 'Ś', 'Ṣ', 'S', 'H'])
  lower.update(upper)
  return lower


ITRANS_ALPHABET = (['a', 'aa', 'i', 'ii', 'u', 'uu', 'Ri', 'RI',
                    'Li', 'LI', 'e', 'ai', 'o', 'au', 'M', 'H',
                    'k', 'kh', 'g', 'gh', '~N',
                    'ch', 'Ch', 'j', 'jh', '~n',
                    'T', 'Th', 'D', 'Dh', 'N',
                    't', 'th', 'd', 'dh', 'n',
                    'p', 'ph', 'b', 'bh', 'm',
                    'y', 'r', 'l', 'v', 'sh', 'Sh', 's', 'h'])


def ITRANSToSLP1Table():
  return AlphabetToSLP1(ITRANS_ALPHABET)


def MangledDevanagariToSLP1StateMachine():
  return transliterate.MakeStateMachine(AlphabetToSLP1(devanagari.Alphabet()))


def TransliterateDevanagari(text):
  return transliterate.Transliterate(MangledDevanagariToSLP1StateMachine(),
                                     devanagari.Mangle(text))


def TransliterateHK(text, pass_through=None):
  return transliterate.Transliterate(HKToSLP1StateMachine(), text, pass_through)


IASTToSLP1Table()
blah = devanagari.Mangle('कगुद')
print blah.encode('utf8')
print [ch for ch in blah]
print TransliterateDevanagari('कगुद')
