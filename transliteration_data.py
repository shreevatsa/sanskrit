# -*- coding: utf-8 -*-

"""Transliteration data."""

from __future__ import unicode_literals

import logging
import re

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


def IASTToSLP1StateMachine():
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
  return transliterate.MakeStateMachine(lower)


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


def TransliterateDevanagari(text):
  return transliterate.Transliterate(MangledDevanagariToSLP1StateMachine(),
                                     devanagari.Mangle(text))


def TransliterateHK(text):
  return transliterate.Transliterate(HKToSLP1StateMachine(), text)


def DetectAndTransliterate(text):
  """Transliterates text to SLP1, after guessing what script it is."""
  characteristic_devanagari = '[%s]' % ''.join(devanagari.Alphabet())
  characteristic_iast = '[āīūṛṝḷḹṅñṭḍṇśṣ]'
  characteristic_itrans = 'aa|ii|uu|R^|~N|~n|N^'
  if re.search(characteristic_devanagari, text):
    logging.info('Reading as Devanāgari.')
    return TransliterateDevanagari(text)
  if re.search(characteristic_iast, text):
    logging.info('Reading as IAST.')
    return transliterate.Transliterate(IASTToSLP1StateMachine(), text)
  if re.search(characteristic_itrans, text):
    logging.info('Reading as ITRANS.')
    return transliterate.Transliterate(ITRANSToSLP1StateMachine(), text)
  logging.info('Reading as Harvard-Kyoto.')
  return transliterate.Transliterate(HKToSLP1StateMachine(), text)
