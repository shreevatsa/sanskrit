# -*- coding: utf-8 -*-

"""Transliteration data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

import devanagari
import slp1
import transliterate


def AlphabetToSLP1(alphabet):
  """Table to SLP1, given a transliteration's alphabet in standard order."""
  return dict(zip(alphabet, slp1.ALPHABET))


def SLP1ToAlphabet(alphabet):
  return dict(zip(slp1.ALPHABET, alphabet))


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


IAST_ALPHABET_LOWER = (list('aāiīuūṛṝḷḹe') + ['ai', 'o', 'au', 'ṃ', 'ḥ'] +
                       ['k', 'kh', 'g', 'gh', 'ṅ',
                        'c', 'ch', 'j', 'jh', 'ñ',
                        'ṭ', 'ṭh', 'ḍ', 'ḍh', 'ṇ',
                        't', 'th', 'd', 'dh', 'n',
                        'p', 'ph', 'b', 'bh', 'm',
                        'y', 'r', 'l', 'v', 'ś', 'ṣ', 's', 'h'])
IAST_ALPHABET_UPPER = (list('AĀIĪUŪṚṜḶḸE') + ['AI', 'O', 'AU', 'Ṃ', 'Ḥ'] +
                       ['K', 'Kh', 'G', 'Gh', 'Ṅ',
                        'C', 'Ch', 'J', 'Jh', 'Ñ',
                        'Ṭ', 'Ṭh', 'Ḍ', 'Ḍh', 'Ṇ',
                        'T', 'Th', 'D', 'Dh', 'N',
                        'P', 'Ph', 'B', 'Bh', 'M',
                        'Y', 'R', 'L', 'V', 'Ś', 'Ṣ', 'S', 'H'])


def IASTToSLP1StateMachine():
  """Transliteration table from IAST to SLP1."""
  lower = AlphabetToSLP1(IAST_ALPHABET_LOWER)
  upper = AlphabetToSLP1(IAST_ALPHABET_UPPER)
  lower.update(upper)
  return transliterate.MakeStateMachine(lower)


def SLP1ToIASTStateMachine():
  return transliterate.MakeStateMachine(SLP1ToAlphabet(IAST_ALPHABET_LOWER))


ITRANS_ALPHABET = (['a', 'aa', 'i', 'ii', 'u', 'uu', 'RRi', 'RRI',
                    'LLi', 'LLI', 'e', 'ai', 'o', 'au', 'M', 'H',
                    'k', 'kh', 'g', 'gh', '~N',
                    'ch', 'Ch', 'j', 'jh', '~n',
                    'T', 'Th', 'D', 'Dh', 'N',
                    't', 'th', 'd', 'dh', 'n',
                    'p', 'ph', 'b', 'bh', 'm',
                    'y', 'r', 'l', 'v', 'sh', 'Sh', 's', 'h'])


def ITRANSToSLP1StateMachine():
  table = AlphabetToSLP1(ITRANS_ALPHABET)
  alternatives = [('aa', 'A'), ('ii', 'I'), ('uu', 'U'), ('RRi', 'R^i'),
                  ('RRI', 'R^I'), ('LLi', 'L^i'), ('LLI', 'L^I'),
                  ('~N', 'N^'), ('~n', 'JN'), ('v', 'w')]
  for (letter, alternative) in alternatives:
    table[alternative] = table[letter]
  return transliterate.MakeStateMachine(table)


def MangledDevanagariToSLP1StateMachine():
  return transliterate.MakeStateMachine(AlphabetToSLP1(devanagari.Alphabet()))


def TransliterateDevanagari(text, ignore=None):
  return transliterate.Transliterate(MangledDevanagariToSLP1StateMachine(),
                                     devanagari.Mangle(text), ignore)


def IsoToIast(text):
  text = text.replace('ṁ', 'ṃ')
  text = text.replace('ē', 'e')
  text = text.replace('ō', 'o')
  text = text.replace('r̥̄', 'ṝ')
  text = text.replace('r̥', 'ṛ')
  text = text.replace('l̥̄', 'ḹ')
  text = text.replace('l̥', 'ḷ')
  return text


def FixBadDevanagari(text):
  text = text.replace('ऎ', 'ए')
  text = text.replace('ऒ', 'ओ')
  text = text.replace('ॆ', 'े')
  text = text.replace('ॊ', 'ो')
  return text


def DetectAndTransliterate(text, ignore=None):
  """Transliterates text to SLP1, after guessing what script it is."""
  text = IsoToIast(text)
  text = FixBadDevanagari(text)
  characteristic_devanagari = '[%s]' % ''.join(devanagari.Alphabet())
  characteristic_iast = '[āīūṛṝḷḹṃḥṅñṭḍṇśṣ]'
  characteristic_itrans = r'aa|ii|uu|[RrLl]\^[Ii]|RR[Ii]|LL[Ii]|~N|Ch|~n|N\^|Sh'
  if re.search(characteristic_devanagari, text):
    return TransliterateDevanagari(text, ignore)
  if re.search(characteristic_iast, text):
    return transliterate.Transliterate(IASTToSLP1StateMachine(), text, ignore)
  if re.search(characteristic_itrans, text):
    return transliterate.Transliterate(ITRANSToSLP1StateMachine(), text, ignore)
  return transliterate.Transliterate(HKToSLP1StateMachine(), text, ignore)


def SLP1ToMangledDevanagariStateMachine():
  return transliterate.MakeStateMachine(SLP1ToAlphabet(devanagari.Alphabet()))


def SLP1ToDevanagari(text):
  (text, _) = transliterate.Transliterate(
      SLP1ToMangledDevanagariStateMachine(), text)
  assert isinstance(text, unicode), text
  return devanagari.UnMangle(text)


def TransliterateForOutput(text):
  return '%s (%s)' % (
      transliterate.Transliterate(SLP1ToIASTStateMachine(), text)[0],
      SLP1ToDevanagari(text))
