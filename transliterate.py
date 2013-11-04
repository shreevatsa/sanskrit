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


def Transliterate(state_machine, text, pass_through = set("-' ")):
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


def TableToSLP1FromAlphabet(alphabet):
  """Table, given a transliteration convention's alphabet in standard order."""
  return dict(zip(alphabet, 'aAiIuUfFxXeEoOMHkKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzsh'))


def HKToSLP1TableNew():
  return TableToSLP1FromAlphabet(list('aAiIuUR') +
                                 ['RR', 'lR', 'lRR', 'e',
                                  'ai', 'o', 'au', 'M', 'H',
                                  'k', 'kh', 'g', 'gh', 'G',
                                  'c', 'ch', 'j', 'jh', 'J',
                                  'T', 'Th', 'D', 'Dh', 'N',
                                  't', 'th', 'd', 'dh', 'n',
                                  'p', 'ph', 'b', 'bh', 'm'] +
                                  list('yrlvzSsh'))


def HKToSLP1Table():
  return {
      'a': 'a',
      'A': 'A',
      'i': 'i',
      'I': 'I',
      'u': 'u',
      'U': 'U',
      'R': 'f',
      'RR': 'F',
      'lR': 'x',
      'lRR': 'X',
      'e': 'e',
      'ai': 'E',
      'o': 'o',
      'au': 'O',
      'M': 'M',
      'H': 'H',
      'k': 'k',
      'kh': 'K',
      'g': 'g',
      'gh': 'G',
      'G': 'N',
      'c': 'c',
      'ch': 'C',
      'j': 'j',
      'jh': 'J',
      'J': 'Y',
      'T': 'w',
      'Th': 'W',
      'D': 'q',
      'Dh': 'Q',
      'N': 'R',
      't': 't',
      'th': 'T',
      'd': 'd',
      'dh': 'D',
      'n': 'n',
      'p': 'p',
      'ph': 'P',
      'b': 'b',
      'bh': 'B',
      'm': 'm',
      'y': 'y',
      'r': 'r',
      'l': 'l',
      'v': 'v',
      'z': 'S',
      'S': 'z',
      's': 's',
      'h': 'h',
  }


print HKToSLP1Table()
print HKToSLP1TableNew()
assert HKToSLP1Table() == HKToSLP1TableNew()
print MakeStateMachine(HKToSLP1Table())
