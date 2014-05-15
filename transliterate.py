# -*- coding: utf-8 -*-

"""Transliteration data."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

import devanagari
import slp1
import transliterator

_DEFAULT_PASS_THROUGH = ' -?'


def _AlphabetToSLP1(alphabet):
  """Table to SLP1, given a transliteration's alphabet in standard order."""
  return dict(zip(alphabet, slp1.ALPHABET))


def _SLP1ToAlphabet(alphabet):
  return dict(zip(slp1.ALPHABET, alphabet))


_HK_ALPHABET = (list('aAiIuUR') + ['RR', 'lR', 'lRR', 'e', 'ai', 'o', 'au'] +
                ['M', 'H',
                 'k', 'kh', 'g', 'gh', 'G',
                 'c', 'ch', 'j', 'jh', 'J',
                 'T', 'Th', 'D', 'Dh', 'N',
                 't', 'th', 'd', 'dh', 'n',
                 'p', 'ph', 'b', 'bh', 'm'] +
                list('yrlvzSsh'))
_HK_TO_SLP1_STATE_MACHINE = transliterator.MakeStateMachine(
    _AlphabetToSLP1(_HK_ALPHABET))


_IAST_ALPHABET_LOWER = (list('aāiīuūṛṝḷḹe') + ['ai', 'o', 'au', 'ṃ', 'ḥ'] +
                        ['k', 'kh', 'g', 'gh', 'ṅ',
                         'c', 'ch', 'j', 'jh', 'ñ',
                         'ṭ', 'ṭh', 'ḍ', 'ḍh', 'ṇ',
                         't', 'th', 'd', 'dh', 'n',
                         'p', 'ph', 'b', 'bh', 'm',
                         'y', 'r', 'l', 'v', 'ś', 'ṣ', 's', 'h'])
_IAST_ALPHABET_UPPER = (list('AĀIĪUŪṚṜḶḸE') + ['AI', 'O', 'AU', 'Ṃ', 'Ḥ'] +
                        ['K', 'Kh', 'G', 'Gh', 'Ṅ',
                         'C', 'Ch', 'J', 'Jh', 'Ñ',
                         'Ṭ', 'Ṭh', 'Ḍ', 'Ḍh', 'Ṇ',
                         'T', 'Th', 'D', 'Dh', 'N',
                         'P', 'Ph', 'B', 'Bh', 'M',
                         'Y', 'R', 'L', 'V', 'Ś', 'Ṣ', 'S', 'H'])


def _IASTToSLP1StateMachine():
  """Transliteration table from IAST to SLP1."""
  lower = _AlphabetToSLP1(_IAST_ALPHABET_LOWER)
  upper = _AlphabetToSLP1(_IAST_ALPHABET_UPPER)
  lower.update(upper)
  return transliterator.MakeStateMachine(lower)
_IAST_TO_SLP1_STATE_MACHINE = _IASTToSLP1StateMachine()


_SLP1_TO_IAST_STATE_MACHINE = transliterator.MakeStateMachine(
    _SLP1ToAlphabet(_IAST_ALPHABET_LOWER))


_ITRANS_ALPHABET = (['a', 'aa', 'i', 'ii', 'u', 'uu', 'RRi', 'RRI',
                     'LLi', 'LLI', 'e', 'ai', 'o', 'au', 'M', 'H',
                     'k', 'kh', 'g', 'gh', '~N',
                     'ch', 'Ch', 'j', 'jh', '~n',
                     'T', 'Th', 'D', 'Dh', 'N',
                     't', 'th', 'd', 'dh', 'n',
                     'p', 'ph', 'b', 'bh', 'm',
                     'y', 'r', 'l', 'v', 'sh', 'Sh', 's', 'h'])


def _ITRANSToSLP1StateMachine():
  table = _AlphabetToSLP1(_ITRANS_ALPHABET)
  alternatives = [('aa', 'A'), ('ii', 'I'), ('uu', 'U'), ('RRi', 'R^i'),
                  ('RRI', 'R^I'), ('LLi', 'L^i'), ('LLI', 'L^I'),
                  ('~N', 'N^'), ('~n', 'JN'), ('v', 'w')]
  for (letter, alternative) in alternatives:
    table[alternative] = table[letter]
  return transliterator.MakeStateMachine(table)
_ITRANS_TO_SLP1_STATE_MACHINE = _ITRANSToSLP1StateMachine()


_MANGLED_DEVANAGARI_TO_SLP1_STATE_MACHINE = transliterator.MakeStateMachine(
    _AlphabetToSLP1(devanagari.Alphabet()))


def _TransliterateDevanagari(text, ignore=None):
  return transliterator.Transliterate(_MANGLED_DEVANAGARI_TO_SLP1_STATE_MACHINE,
                                      devanagari.Mangle(text), ignore,
                                      _DEFAULT_PASS_THROUGH)


def _IsoToIast(text):
  text = text.replace('ṁ', 'ṃ')
  text = text.replace('ē', 'e')
  text = text.replace('ō', 'o')
  text = text.replace('r̥̄', 'ṝ')
  text = text.replace('r̥', 'ṛ')
  text = text.replace('l̥̄', 'ḹ')
  text = text.replace('l̥', 'ḷ')
  return text


def _FixBadDevanagari(text):
  # TODO(shreevatsa): Warn about these "wrong" characters.
  text = text.replace('ऎ', 'ए')
  text = text.replace('ऒ', 'ओ')
  text = text.replace('ॆ', 'े')
  text = text.replace('ॊ', 'ो')
  text = text.replace('ळ', 'ल')
  text = text.replace('ॐ', 'ओं')
  return text


def DetectAndTransliterate(text, pass_through=None, ignore=None):
  """Transliterates text to SLP1, after guessing what script it is."""
  text = _IsoToIast(text)
  text = _FixBadDevanagari(text)
  characteristic_devanagari = '[%s]' % ''.join(devanagari.Alphabet())
  characteristic_iast = '[āīūṛṝḷḹṃḥṅñṭḍṇśṣ]'
  characteristic_itrans = r'aa|ii|uu|[RrLl]\^[Ii]|RR[Ii]|LL[Ii]|~N|Ch|~n|N\^|Sh'
  if re.search(characteristic_devanagari, text):
    text = text.replace('s', 'ऽ')
    return _TransliterateDevanagari(text, ignore)
  if re.search(characteristic_iast, text):
    return transliterator.Transliterate(_IAST_TO_SLP1_STATE_MACHINE,
                                        text, ignore, pass_through)
  if re.search(characteristic_itrans, text):
    return transliterator.Transliterate(_ITRANS_TO_SLP1_STATE_MACHINE,
                                        text, ignore, pass_through)
  ret = transliterator.Transliterate(_HK_TO_SLP1_STATE_MACHINE, text,
                                     ignore, pass_through)
  return ret


_SLP1_TO_MANGLED_DEVANAGARI_STATE_MACHINE = transliterator.MakeStateMachine(
    _SLP1ToAlphabet(devanagari.Alphabet()))


def _CleanSLP1ToDevanagari(text):
  (text, unparsed) = transliterator.Transliterate(
      _SLP1_TO_MANGLED_DEVANAGARI_STATE_MACHINE, text, ignore=None,
      pass_through=_DEFAULT_PASS_THROUGH)
  assert not unparsed, (text, unparsed)
  assert isinstance(text, unicode), text
  return devanagari.UnMangle(text)


def TransliterateForOutput(text):
  iast = transliterator.Transliterate(_SLP1_TO_IAST_STATE_MACHINE, text,
                                      ignore=None,
                                      pass_through=_DEFAULT_PASS_THROUGH)[0]
  deva = _CleanSLP1ToDevanagari(text)
  return '%s (%s)' % (iast, deva)


def AddDevanagariToIast(iast):
  """Given IAST text, include the Devanagari transliteration in brackets."""
  stray = ' ()/'      # Non-IAST characters that appear in metre names
  slp_text = transliterator.Transliterate(_IAST_TO_SLP1_STATE_MACHINE, iast,
                                          ignore=None, pass_through=stray)[0]
  (deva, unparsed) = transliterator.Transliterate(
      _SLP1_TO_MANGLED_DEVANAGARI_STATE_MACHINE, slp_text, ignore=None,
      pass_through=stray)
  assert not unparsed, (deva, unparsed)
  assert isinstance(deva, unicode), deva
  deva = devanagari.UnMangle(deva)
  return '%s (%s)' % (iast, deva)


def TransliterateForTable(text):
  return transliterator.Transliterate(_SLP1_TO_IAST_STATE_MACHINE, text,
                                      ignore=None,
                                      pass_through=_DEFAULT_PASS_THROUGH)[0]
