# -*- coding: utf-8 -*-
"""Data structures that store matching metres for known patterns."""

from __future__ import absolute_import, division, print_function, unicode_literals

import itertools
import re
import unicodedata

import data.ganesh
import data.curated
import data.dhaval
import data.dhaval_vrttaratnakara
from print_utils import Print

known_full_patterns = {}
known_full_regexes = []

known_half_patterns = {}
known_half_regexes = []

known_pada_patterns = {}
known_pada_regexes = []

pattern_for_metre = {}
all_data = {}


def GetPattern(metre):
  return pattern_for_metre.get(metre)


def _RemoveChars(input_string, chars):
  """Wrapper function because string.translate != unicode.translate."""
  for char in chars:
    input_string = input_string.replace(char, '')
  return input_string


def _CleanUpPattern(pattern):
  pattern = _RemoveChars(pattern, [unicodedata.lookup('SPACE'), unicodedata.lookup('EM DASH'), unicodedata.lookup('EN DASH')])
  assert re.match(r'^[LG]*$', pattern), pattern
  return pattern


def _CleanUpSimpleRegex(regex):
  regex = _RemoveChars(regex, [unicodedata.lookup('SPACE'), unicodedata.lookup('EM DASH'), unicodedata.lookup('EN DASH')])
  assert re.match(r'^[LG.]*$', regex), regex
  return regex


def _AddPatternForMetre(metre_name, pada_patterns):
  if metre_name in pattern_for_metre:
    if pattern_for_metre[metre_name] != pada_patterns:
      Print('Mismatch for %s' % metre_name)
      Print(pattern_for_metre[metre_name])
      Print('   vs   ')
      Print(pada_patterns)
      assert False
    # Print('Not adding duplicate as already present: %s' % metre_name)
    return
  pattern_for_metre[metre_name] = pada_patterns


def _AddFullPattern(full_pattern, metre_name):
  if full_pattern in known_full_patterns:
    # TODO(shreevatsa): Figure out what exactly to do in this case
    Print('Error: full pattern already present')
    Print(metre_name)
    Print(full_pattern)
    Print(known_full_patterns[full_pattern])
    return False
  assert full_pattern not in known_full_patterns
  known_full_patterns[full_pattern] = {metre_name: True}
  return True

def _AddHalfPattern(half_pattern, metre_name, which_halves):
  known_half_patterns.setdefault(half_pattern, {}).setdefault(metre_name, set()).update(which_halves)

def _AddPadaPattern(pada_pattern, metre_name, which_padas):
  known_pada_patterns.setdefault(pada_pattern, {}).setdefault(metre_name, set()).update(which_padas)

def _AddSamavrttaPattern(metre_name, each_pada_pattern):
  """Given a sama-vṛtta metre's pattern, add it to the data structures."""
  clean = _CleanUpPattern(each_pada_pattern)
  assert re.match(r'^[LG]*G$', clean), (each_pada_pattern, metre_name)
  _AddPatternForMetre(metre_name, [clean] * 4)

  patterns = [clean[:-1] + 'G', clean[:-1] + 'L']
  for (a, b, c, d) in itertools.product(patterns, repeat=4): _AddFullPattern(a + b + c + d, metre_name)
  for (a, b) in itertools.product(patterns, repeat=2): _AddHalfPattern(a + b, metre_name, {1, 2})
  for a in patterns: _AddPadaPattern(a, metre_name, {1, 2, 3, 4})


def _AddArdhasamavrttaPattern(metre_name, odd_and_even_pada_patterns):
  """Given an ardha-sama-vṛtta's pattern, add it."""
  (odd_pada_pattern, even_pada_pattern) = odd_and_even_pada_patterns
  clean_odd = _CleanUpPattern(odd_pada_pattern)
  assert re.match(r'^[LG]*$', clean_odd)
  clean_even = _CleanUpPattern(even_pada_pattern)
  if clean_even.endswith('L'):
    Print('Not adding %s for now, as %s ends with laghu' % (metre_name, clean_even))
    return
  assert re.match(r'^[LG]*G$', clean_even), (metre_name, clean_even)
  _AddPatternForMetre(metre_name, [clean_odd, clean_even] * 2)

  patterns_odd = [clean_odd[:-1] + 'G', clean_odd[:-1] + 'L']
  patterns_even = [clean_even[:-1] + 'G', clean_even[:-1] + 'L']
  for (a, b, c, d) in itertools.product(patterns_odd, patterns_even, repeat=2): _AddFullPattern(a + b + c + d, metre_name)
  for (a, b) in itertools.product(patterns_odd, patterns_even): _AddHalfPattern(a + b, metre_name, {1, 2})
  for a in patterns_odd: _AddPadaPattern(a, metre_name, {1, 3})
  for b in patterns_even: _AddPadaPattern(b, metre_name, {2, 4})


def _AddVishamavrttaPattern(metre_name, pada_patterns):
  """Given the four pāda-s of a viṣama-vṛtta, add the metre."""
  assert len(pada_patterns) == 4
  pada_patterns = [_CleanUpPattern(p) for p in pada_patterns]
  for p in pada_patterns: assert re.match(r'^[LG]*$', p)
  (pa, pb, pc, pd) = pada_patterns
  assert pb.endswith('G')
  assert pd.endswith('G')
  _AddPatternForMetre(metre_name, [pa, pb, pc, pd])

  patterns_a = [pa]
  patterns_b = [pb[:-1] + 'G', pb[:-1] + 'L']
  patterns_c = [pc]
  patterns_d = [pd[:-1] + 'G', pd[:-1] + 'L']
  for (a, b, c, d) in itertools.product(patterns_a, patterns_b, patterns_c, patterns_d): _AddFullPattern(a + b + c + d, metre_name)
  for (a, b) in itertools.product(patterns_a, patterns_b): _AddHalfPattern(a + b, metre_name, {1})
  for (c, d) in itertools.product(patterns_c, patterns_d): _AddHalfPattern(c + d, metre_name, {2})
  for a in patterns_a: _AddPadaPattern(a, metre_name, {1})
  for b in patterns_b: _AddPadaPattern(b, metre_name, {2})
  for c in patterns_c: _AddPadaPattern(c, metre_name, {3})
  for d in patterns_d: _AddPadaPattern(d, metre_name, {4})


def _AddFullRegex(full_verse_regex, metre_name):
  known_full_regexes.append((re.compile('^' + full_verse_regex + '$'), {metre_name : True}))


def _AddHalfRegex(half_verse_regex, metre_name, which_halves):
  known_half_regexes.append((re.compile('^' + half_verse_regex + '$'), {metre_name: which_halves}))


def _AddPadaRegex(pada_regex, metre_name, which_padas):
  known_pada_regexes.append((re.compile('^' + pada_regex + '$'), {metre_name: which_padas}))


def _AddSamavrttaRegex(metre_name, pada_regex):
  """Add a sama-vṛtta's regex (full, half, pāda). No variants."""
  pada_regex = _CleanUpSimpleRegex(pada_regex)
  _AddFullRegex(''.join('(%s)' % s for s in [pada_regex] * 4), metre_name)
  _AddHalfRegex(''.join('(%s)' % s for s in [pada_regex] * 2), metre_name, {1, 2})
  _AddPadaRegex(pada_regex, metre_name, {1, 2, 3, 4})


def _AddMetreRegex(metre_name, pada_regexes, simple=True):
  """Given regexes for the four padas of a metre, add it."""
  assert len(pada_regexes) == 4, (metre_name, pada_regexes)
  if simple:
    pada_regexes = [_CleanUpSimpleRegex(s) for s in pada_regexes]
  full_verse_regex = ''.join('(%s)' % s for s in pada_regexes)
  _AddFullRegex(full_verse_regex, metre_name)


def _AddAnustup():
  """Add Anuṣṭup to the list of regexes."""
  metre_name = 'Anuṣṭup (Śloka)'
  regex_ac = '....LGG.'
  regex_bd = '....LGL.'
  half_regex = regex_ac + regex_bd

  _AddFullRegex(half_regex * 2, metre_name)
  _AddHalfRegex(half_regex, metre_name, {1, 2})
  _AddPadaRegex(regex_ac, metre_name, {1, 3})
  _AddPadaRegex(regex_bd, metre_name, {2, 4})


def _AddAnustupExamples():
  """Examples of variation from standard Anuṣṭup."""
  # "jayanti te sukṛtino..."
  _AddMetreRegex('Anuṣṭup (Śloka)',
                 ['LGLGLLLG', '....LGL.', '....LGG.', '....LGL.'])
  # "sati pradīpe saty agnau..." Proof: K48.130 (p. 51)
  _AddMetreRegex('Anuṣṭup (Śloka)',
                 ['LGLGGGGG', '....LGL.', '....LGG.', '....LGL.'])
  # "guruṇā stana-bhāreṇa [...] śanaiś-carābhyāṃ pādābhyāṃ" K48.132 (52)
  _AddMetreRegex('Anuṣṭup (Śloka)',
                 ['....LGG.', '....LGL.', 'LGLGGGGG', '....LGL.'])
  # "tāvad evāmṛtamayī..." K48.125 (49)
  _AddMetreRegex('Anuṣṭup (Śloka)',
                 ['GLGGLLLG', '....LGL.', '....LGG.', '....LGL.'])
  # Covers a lot of cases
  _AddMetreRegex('Anuṣṭup (Śloka)',
                 ['........', '....LGL.', '....LGG.', '....LGL.'])
  _AddMetreRegex('Anuṣṭup (Śloka)',
                 ['....LGG.', '....LGL.', '........', '....LGL.'])
  _AddMetreRegex('Anuṣṭup (Śloka)',
                 ['........', '....LGL.', '........', '....LGL.'])


def _MatraCount(pattern):
  assert re.match('^[LG]*$', pattern)
  return sum(2 if c == 'G' else 1 for c in pattern)


def _PatternsOfLength(n):
  if n in _patterns_memo:
    return _patterns_memo[n]
  _patterns_memo[n] = [p + 'L' for p in _PatternsOfLength(n - 1)]
  _patterns_memo[n] += [p + 'G' for p in _PatternsOfLength(n - 2)]
  return _patterns_memo[n]
_patterns_memo = {0: [''], 1: ['L']}


def _LoosePatternsOfLength(n):
  if n in _loose_patterns_memo:
    return _loose_patterns_memo[n]
  _loose_patterns_memo[n] = (_PatternsOfLength(n) +
                             [p for p in _PatternsOfLength(n - 1)
                              if p.endswith('L')])
  return _loose_patterns_memo[n]
_loose_patterns_memo = {0: [''], 1: ['L']}


def _AddAryaFamilyRegex():
  """Add regexes for the Āryā family of metres."""
  odd_ganas = ['GG', 'LLG', 'GLL', 'LLLL']
  even_ganas = odd_ganas + ['LGL']
  odd_gana_re = '(%s)' % '|'.join(odd_ganas)
  even_gana_re = '(%s)' % '|'.join(even_ganas)
  pada_12_re = odd_gana_re + even_gana_re + odd_gana_re
  pada_15_re = even_gana_re + odd_gana_re + 'L' + odd_gana_re + '(L|G)'
  pada_18_re = even_gana_re + odd_gana_re + '(LLLL|LGL)' + odd_gana_re + '(L|G)'
  pada_20_re = (even_gana_re + odd_gana_re + '(LLLL|LGL)' + odd_gana_re +
                '(%s)' % '|'.join(even_ganas + ['GL', 'LLL']))
  _AddMetreRegex('Āryā',
                 [pada_12_re, pada_18_re, pada_12_re, pada_15_re], simple=False)
  _AddMetreRegex('Gīti',
                 [pada_12_re, pada_18_re, pada_12_re, pada_18_re], simple=False)
  _AddMetreRegex('Upagīti',
                 [pada_12_re, pada_15_re, pada_12_re, pada_15_re], simple=False)
  _AddMetreRegex('Udgīti',
                 [pada_12_re, pada_15_re, pada_12_re, pada_18_re], simple=False)
  _AddMetreRegex('Āryāgīti',
                 [pada_12_re, pada_20_re, pada_12_re, pada_20_re], simple=False)
  _AddMetreRegex('Āryā (loose schema)',
                 ['|'.join(_LoosePatternsOfLength(12)),
                  '|'.join(_LoosePatternsOfLength(18)),
                  '|'.join(_LoosePatternsOfLength(12)),
                  '|'.join(_LoosePatternsOfLength(15))],
                 simple=False)


def _AddGiti(pada_patterns):
  """Add an example of Gīti, with proper morae checking."""
  assert len(pada_patterns) == 4
  expected = [12, 18, 12, 18]
  for i in range(4):
    allow_loose_ending = False
    if i % 2 and pada_patterns[i].endswith('L'):
      allow_loose_ending = True
      expected[i] -= 1
    assert _MatraCount(pada_patterns[i]) == expected[i], (i, pada_patterns[i], _MatraCount(pada_patterns[i]), expected[i])
    if allow_loose_ending:
      pada_patterns[i] = pada_patterns[i][:-1] + '.'
  # TODO(shreevatsa): Should we just add (up to) 4 patterns instead?
  _AddMetreRegex('Gīti', pada_patterns, simple=False)


def _AddKarambajati():
  """Examples of Upajāti of Vaṃśastham and Indravaṃśā."""
  # _AddSamavrttaPattern('Vaṃśastham (Vaṃśasthavila)', 'LGLGGLLGLGLG')
  # _AddSamavrttaPattern('Indravaṃśā', 'G G L G G L L G L G L G')
  # Also add all their Upajāti mixtures, with the above two 0000 and 1111
  _AddSamavrttaRegex('Vaṃśastham/Indravaṃśā', '. G L G G L L G L G L .')
  # # 0001
  # AddExactVrtta('Śīlāturā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['LGLGGLLGLGLG',
  #                'LGLGGLLGLGLG',
  #                'LGLGGLLGLGLG',
  #                'GGLGGLLGLGLG'])
  # # 0010
  # AddExactVrtta('Vaidhātrī (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])
  # # 0011
  # AddExactVrtta('Indumā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'])
  # # 0100
  # AddExactVrtta('Ramaṇā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])
  # # 0101
  # AddExactVrtta('Upameyā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'] * 2)
  # # 0110
  # AddExactVrtta('Manahāsā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])
  # # 0111
  # AddExactVrtta('Varāsikā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'])
  # # 1000
  # AddExactVrtta('Kumārī (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])
  # # 1001
  # AddExactVrtta('Saurabheyī (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'])
  # # 1010
  # AddExactVrtta('Śiśirā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'] * 2)
  # # 1011
  # AddExactVrtta('Ratākhyānakī (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'])
  # # 1100
  # AddExactVrtta('Śaṅkhacūḍā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])
  # # 1101
  # AddExactVrtta('Puṣṭidā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G',
  #                'G G L G G L L G L G L G'])
  # # 1110
  # AddExactVrtta('Vāsantikā (Upajāti of Vaṃśastham and Indravaṃśā)',
  #               ['G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'G G L G G L L G L G L G',
  #                'L G L G G L L G L G L G'])


def InitializeData():
  """Add all known metres to the data structures."""
  _AddAnustup()
  _AddAnustupExamples()

  _AddAryaFamilyRegex()
  _AddKarambajati()

  vrtta_data = (data.ganesh.data
                + data.curated.curated_vrtta_data
                + data.dhaval_vrttaratnakara.data_vrttaratnakara
                # + data.dhaval.dhaval_vrtta_data
                )

  assert not all_data
  for (name, description) in vrtta_data:
    samatva = None
    regex_or_pattern = None
    if isinstance(description, list):
      assert len(description) in [2, 4]
      samatva = 'ardhasama' if len(description) == 2 else 'viṣama'
      regex_or_pattern = 'pattern'
    else:
      samatva = 'sama'
      if re.match(r'^[LG]*$', _RemoveChars(description, ' —–')):
        regex_or_pattern = 'pattern'
      else:
        regex_or_pattern = 'regex'

    assert samatva in ['sama', 'ardhasama', 'viṣama']
    assert regex_or_pattern in ['regex', 'pattern']
    all_data[name] = (samatva, regex_or_pattern, description)

    if samatva == 'sama' and regex_or_pattern == 'regex':
      _AddSamavrttaRegex(name, description)
    elif samatva == 'sama' and regex_or_pattern == 'pattern':
      _AddSamavrttaPattern(name, description)
    elif samatva == 'ardhasama' and regex_or_pattern == 'pattern':
      _AddArdhasamavrttaPattern(name, description)
    elif samatva == 'viṣama' and regex_or_pattern == 'pattern':
      _AddVishamavrttaPattern(name, description)
    else:
      assert False, name


def HtmlDescription(name):
  if name not in all_data:
    return '[No description currently for %s]' % name
  (samatva, regex_or_pattern, description) = all_data[name]
  if regex_or_pattern == 'regex':
    return '[%s is given by the regex %s]' % (name, description)
  assert regex_or_pattern == 'pattern'
  if samatva == 'sama':
    return ('%s is a sama-vṛtta. It contains 4 <i>pāda</i>s, each of which' +
            '  has the pattern %s') % (name, description)
  elif samatva == 'ardhasama':
    assert isinstance(description, list)
    assert len(description) == 2
    return ('%s is an ardha-sama-vṛtta. It contains 4 <i>pāda</i>s, in which' +
            ' the odd <i>pāda</i>s have pattern:<br/>' +
            '%s<br/>'
            ' and the even <i>pāda</i>s have pattern:<br/>' +
            '%s') % (name, description[0], description[1])
  else:
    assert samatva == 'viṣama'
    assert isinstance(description, list)
    assert len(description) == 4
    return ('%s is a viṣama-vṛtta. It contains 4 <i>pāda</i>s, which have' +
            ' respectively the patterns:<br>' +
            '%s<br/>' +
            '%s<br/>' +
            '%s<br/>' +
            '%s') % (name, description[0], description[1],
                     description[2], description[3])
