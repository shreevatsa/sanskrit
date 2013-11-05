# -*- coding: utf-8 -*-

"""Transliteration.

The simplest case of transliteration is when each character of input corresponds
to a unique character of output. When you see 'e' output <e>, when you see 'y'
output <y>, etc. In this case the code would be rather simple too: set up a
"replacement" lookup table, and

    t = ''.join(replacement[c] for c in s)

The wrinkle, which prevents this approach from working, is cases where we may
not be able to output until seeing more characters of input. When you see 'a',
you need to wait and see whether the next character is 'i'; can't output based
on seeing 'k' without waiting to check whether the next character is 'h'.

This can be solved by ordering and applying the substitution rules in, say,
descending order of length (so that 'ai' occurs before 'a').

Another solution (which we use) is to create and run a state machine. When you
see 'e' from the default state, output <e> and return to the default state, but
when you see 'k', go into a state where

- if the next character is 'h', output 'kh' and go to the default state (having
  consumed both characters)

- if the next character is anything else, output 'k', and go to the default
  state *without* consuming the character.

So each "state" is a dict containing two values for every "key" (character): on
seeing that character, which state to go to, and how many characters to consume.
"""

from __future__ import unicode_literals

import devanagari


def MakeStateMachine(table):
  """Makes SM from a dict like {'a':'अ', 'A':'आ', 'ai':'ऐ', 'au':'औ'}."""
  root = {}
  for (key, value) in table.iteritems():
    # Follow characters of 'key' down the table
    where = root
    for c in key: where = where.setdefault(c, {})
    where[''] = value
  return root


def FirstLongestMatch(state_machine, text):
  """Finds longest match from state machine at start of the text."""
  where = state_machine
  num_seen = 0
  num_matched = 0
  replacement = None
  for c in text:
    num_seen += 1
    where = where.get(c)
    if not where: return (num_matched, replacement)
    if where.has_key(''):
      num_matched = num_seen
      replacement = where['']
  return (num_matched, replacement)


def Transliterate(state_machine, text, pass_through="-' "):
  """Transliterates text using the state machine."""
  transliterated = ''
  unparsed_positions = set()
  num_parsed = 0
  while num_parsed < len(text):
    (num_matched, replacement) = FirstLongestMatch(state_machine,
                                                   text[num_parsed:])
    if num_matched == 0:
      if text[num_parsed] in pass_through:
        transliterated += text[num_parsed]
      else:
        unparsed_positions.add(num_parsed)
      num_parsed += 1
    else:
      transliterated += replacement
      num_parsed += num_matched
  return (transliterated, unparsed_positions)


def AlphabetToSLP1(alphabet):
  """Table, given a transliteration convention's alphabet in standard order."""
  return dict(zip(alphabet,
                  'aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh'))


def HKToSLP1Table():
  return AlphabetToSLP1(list('aAiIuUR') +
                        ['RR', 'lR', 'lRR', 'e', 'ai', 'o', 'au', 'M', 'H',
                         'k', 'kh', 'g', 'gh', 'G',
                         'c', 'ch', 'j', 'jh', 'J',
                         'T', 'Th', 'D', 'Dh', 'N',
                         't', 'th', 'd', 'dh', 'n',
                         'p', 'ph', 'b', 'bh', 'm'] +
                        list('yrlvzSsh'))


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
  upper.update(lower)
  assert lower == upper
  return lower


def ITRANSToSLP1Table():
  return AlphabetToSLP1(['a', 'aa', 'i', 'ii', 'u', 'uu', 'Ri', 'RI',
                         'Li', 'LI', 'e', 'ai', 'o', 'au', 'M', 'H',
                         'k', 'kh', 'g', 'gh', '~N',
                         'ch', 'Ch', 'j', 'jh', '~n',
                         'T', 'Th', 'D', 'Dh', 'N',
                         't', 'th', 'd', 'dh', 'n',
                         'p', 'ph', 'b', 'bh', 'm',
                         'y', 'r', 'l', 'v', 'sh', 'Sh', 's', 'h'])


def MangledDevanagariToSLP1Table():
  return AlphabetToSLP1(devanagari.Alphabet())


def TransliterateDevanagari(text):
  return Transliterate(MakeStateMachine(MangledDevanagariToSLP1Table()),
                       devanagari.Mangle(text))


print MakeStateMachine(HKToSLP1Table())
print MakeStateMachine(IASTToSLP1Table())
blah = devanagari.Mangle('कगुद')
print blah, [ch for ch in blah]
print TransliterateDevanagari('कगुद')
