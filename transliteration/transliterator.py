# -*- coding: utf-8 -*-

"""The algorithm / machine for transliteration.

The simplest case of transliteration is when each character of input corresponds
to a unique string of output. When you see 'e' output <e>, when you see 'y'
output <y>, etc. In this case the code would be rather simple too: set up a
"replacement" lookup table, and

    t = ''.join(replacement[c] for c in s)

The wrinkle that prevents such an approach from working is that in our case, you
may not be able to output until seeing multiple characters of input. When you
see 'a', you need to wait and see whether the next character is 'i'. And on
seeing 'k', you still need to check whether the next character is 'h'.

This can be solved by ordering and applying the substitution rules in, say,
descending order of length (so that 'ai' occurs before 'a').

Another solution (which we use) is to create and run a state machine. When you
see 'e' when in the default state, output <e> and return to the default state,
but when you see 'k', go into a state where

- if the next character is 'h', output <kh> and go to the default state (having
  consumed both characters)

- if the next character is anything else, output <k>, and go to the default
  state (having consumed only the 'k').

So each "state" is a dict containing two values for every "key" (character): on
seeing that character, which state to go to, and how many characters to consume.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


def MakeStateMachine(table):
  """Makes SM from a dict like {'a':'अ', 'A':'आ', 'ai':'ऐ', 'au':'औ'}."""
  root = {}
  for (key, value) in table.items():
    # Follow characters of 'key' down the table
    where = root
    for c in key:
      where = where.setdefault(c, {})
    where[''] = value
  return root


def _LongestRead(state_machine, text):
  """Finds longest match from state machine at start of the text."""
  where = state_machine
  num_seen = 0
  num_matched = 0
  replacement = None
  for c in text:
    num_seen += 1
    where = where.get(c)
    if not where:
      return (num_matched, replacement)
    if '' in where:  # If there's a key that terminates here
      num_matched = num_seen
      replacement = where['']
  return (num_matched, replacement)


def Transliterate(state_machine, text, pass_through=None):
  """Transliterates text using the state machine."""
  transliterated = ''
  unparsed_characters = set()
  num_parsed = 0
  while num_parsed < len(text):
    # TODO(shreevatsa): Is text[num_parsed:] doing many copies for long text?
    (num_matched, replacement) = _LongestRead(state_machine, text[num_parsed:])
    if num_matched > 0:
      transliterated += replacement
      num_parsed += num_matched
    else:
      # Couldn't match anything; strip one char and retry.
      char = text[num_parsed]
      if pass_through and char in pass_through:
        transliterated += char
      else:
        unparsed_characters.add(char)
      num_parsed += 1
  return (transliterated, unparsed_characters)
