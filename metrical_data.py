# -*- coding: utf-8 -*-
"""Data structures that store matching metres for known patterns."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import re

import match_result


known_metre_regexes = []
known_metre_patterns = {}
known_partial_regexes = []
known_partial_patterns = {}
pattern_for_metre = {}


def _RemoveChars(input_string, chars):
  """Wrapper function because string.translate != unicode.translate."""
  for char in chars:
    input_string = input_string.replace(char, '')
  return input_string


def _CleanUpPattern(pattern):
  pattern = _RemoveChars(pattern, ' —–')
  assert re.match(r'^[LG]*$', pattern), pattern
  return pattern


def _CleanUpSimpleRegex(regex):
  regex = _RemoveChars(regex, ' —–')
  assert re.match(r'^[LG.]*$', regex), regex
  return regex


def GetPattern(metre):
  return pattern_for_metre.get(metre)


def _AddSamavrttaPattern(metre_name, each_line_pattern):
  """Given a sama-vṛtta metre's pattern, add it to the data structures."""
  clean = _CleanUpPattern(each_line_pattern)
  assert re.match(r'^[LG]*G$', clean), (each_line_pattern, metre_name)
  assert metre_name not in pattern_for_metre
  pattern_for_metre[metre_name] = [clean] * 4
  patterns = [clean[:-1] + 'G', clean[:-1] + 'L']
  for (a, b, c, d) in itertools.product(patterns, repeat=4):
    assert (a + b + c + d) not in known_metre_patterns
    known_metre_patterns[a + b + c + d] = match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.FULL)
  for (a, b) in itertools.product(patterns, repeat=2):
    assert a + b not in known_partial_patterns
    known_partial_patterns[a + b] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.HALF)]
  for a in patterns:
    known_partial_patterns[a] = known_partial_patterns.get(a, []).append(
        match_result.MatchResult(metre_name, match_result.MATCH_TYPE.PADA))


def _AddArdhasamavrttaPattern(metre_name, odd_and_even_line_patterns):
  """Given an ardha-sama-vṛtta metres' pattern, add it."""
  (odd_line_pattern, even_line_pattern) = odd_and_even_line_patterns
  clean_odd = _CleanUpPattern(odd_line_pattern)
  assert re.match(r'^[LG]*G$', clean_odd)
  clean_even = _CleanUpPattern(even_line_pattern)
  assert re.match(r'^[LG]*G$', clean_even)
  assert metre_name not in pattern_for_metre
  pattern_for_metre[metre_name] = [clean_odd, clean_even] * 2
  patterns_odd = [clean_odd[:-1] + 'G', clean_odd[:-1] + 'L']
  patterns_even = [clean_even[:-1] + 'G', clean_even[:-1] + 'L']
  for (a, b, c, d) in itertools.product(patterns_odd, patterns_even, repeat=2):
    assert (a + b + c + d) not in known_metre_patterns
    known_metre_patterns[a + b + c + d] = match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.FULL)
  for (a, b) in itertools.product(patterns_odd, patterns_even):
    assert a + b not in known_partial_patterns
    known_partial_patterns[a + b] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.HALF)]
  for a in patterns_odd:
    assert a not in known_partial_patterns
    known_partial_patterns[a] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.ODD_PADA)]
  for a in patterns_even:
    assert a not in known_partial_patterns
    known_partial_patterns[a] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.EVEN_PADA)]


def _AddVishamavrttaPattern(metre_name, line_patterns):
  """Given the four lines of a viṣama-vṛtta, add the metre."""
  assert len(line_patterns) == 4
  line_patterns = [_CleanUpPattern(p) for p in line_patterns]
  for p in line_patterns:
    assert re.match(r'^[LG]*$', p)
  (pa, pb, pc, pd) = line_patterns
  assert pb.endswith('G')
  assert pd.endswith('G')
  assert metre_name not in pattern_for_metre
  pattern_for_metre[metre_name] = pa + pb + pc + pd
  patterns_a = [pa]
  patterns_b = [pb[:-1] + 'G', pb[:-1] + 'L']
  patterns_c = [pc]
  patterns_d = [pd[:-1] + 'G', pd[:-1] + 'L']
  for (a, b, c, d) in itertools.product(patterns_a, patterns_b,
                                        patterns_c, patterns_d):
    assert (a + b + c + d) not in known_metre_patterns
    known_metre_patterns[a + b + c + d] = match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.FULL)
  for (a, b) in itertools.product(patterns_a, patterns_b):
    assert a + b not in known_metre_patterns
    known_partial_patterns[a + b] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.FIRST_HALF)]
  for (c, d) in itertools.product(patterns_c, patterns_d):
    assert c + d not in known_partial_patterns
    known_partial_patterns[c + d] = [match_result.MatchResult(
        metre_name, match_result.MATCH_TYPE.SECOND_HALF)]


def _AddMetreRegex(metre_name, line_regexes, simple=True):
  """Given regexes for the four lines of a metre, add it."""
  assert len(line_regexes) == 4, (metre_name, line_regexes)
  if simple:
    line_regexes = [_CleanUpSimpleRegex(s) for s in line_regexes]
  full_verse_regex = ''.join('(%s)' % s for s in line_regexes)
  match = match_result.MatchResult(metre_name, match_result.MATCH_TYPE.FULL)
  known_metre_regexes.append((re.compile('^' + full_verse_regex + '$'), match))


def _AddSamavrttaRegex(metre_name, line_regex):
  """Add a sama-vṛtta's regex (full, half, pāda). No variants."""
  line_regex = _CleanUpSimpleRegex(line_regex)
  full_verse_regex = ''.join('(%s)' % s for s in [line_regex] * 4)
  match = match_result.MatchResult(metre_name, match_result.MATCH_TYPE.FULL)
  known_metre_regexes.append((re.compile('^' + full_verse_regex + '$'), match))
  half_verse_regex = ''.join('(%s)' % s for s in [line_regex] * 2)
  match = match_result.MatchResult(metre_name, match_result.MATCH_TYPE.HALF)
  known_partial_regexes.append((re.compile('^' + half_verse_regex + '$'),
                                match))
  match = match_result.MatchResult(metre_name, match_result.MATCH_TYPE.PADA)
  known_partial_regexes.append((re.compile('^' + line_regex + '$'), match))


def _AddAnustup():
  """Add Anuṣṭup to the list of regexes."""
  regex_ac = '....LGG.'
  regex_bd = '....LGL.'
  half_regex = regex_ac + regex_bd
  full_regex = half_regex * 2

  match = match_result.MatchResult('Anuṣṭup (Śloka)',
                                   match_result.MATCH_TYPE.FULL)
  known_metre_regexes.append((re.compile('^' + full_regex + '$'), match))

  match = match_result.MatchResult('Anuṣṭup (Śloka)',
                                   match_result.MATCH_TYPE.HALF)
  known_partial_regexes.append((re.compile('^' + half_regex + '$'), match))

  match = match_result.MatchResult('Anuṣṭup (Śloka)',
                                   match_result.MATCH_TYPE.ODD_PADA)
  known_partial_regexes.append((re.compile('^' + regex_ac + '$'), match))

  match = match_result.MatchResult('Anuṣṭup (Śloka)',
                                   match_result.MATCH_TYPE.EVEN_PADA)
  known_partial_regexes.append((re.compile('^' + regex_bd + '$'), match))


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


def _AddArya(line_patterns):
  """Add an example of Arya, with proper morae checking."""
  assert len(line_patterns) == 4
  expected = [12, 18, 12, 15]
  for i in range(4):
    allow_loose_ending = False
    if i % 2 and line_patterns[i].endswith('L'):
      allow_loose_ending = True
      expected[i] -= 1
    assert _MatraCount(line_patterns[i]) == expected[i]
    if allow_loose_ending:
      line_patterns[i] = line_patterns[i][:-1] + '.'
  # TODO(shreevatsa): Should we just add (up to) 4 patterns instead?
  _AddMetreRegex('Āryā', line_patterns, simple=False)


def _AddAryaExamples():
  """Add collected examples of the Āryā metre."""
  # From Bhartṛhari (BharSt_1.3, ajñaḥ sukham ārādhyaḥ...)
  _AddArya(['GGLLGGG', 'LLLLGGLGLGGG', 'GLLLGLGG', 'GGLLGLGLLL'])
  # From Bhartṛhari (BharSt_1.37, siṃhaḥ śiśur api nipatati...)
  _AddArya(['GGLLLLLLLL', 'LLLLLLGLGLLLGG', 'LLLLGGLLG', 'LLLLGGLGGL'])
  # From Bhartṛhari (BharSt_1.43, dānaṃ bhogo nāśas...)
  _AddArya(['GGGGGG', 'GGLLGLGLGGL', 'GLLGLLGG', 'GLLGGLGLLL'])
  # From Bhartṛhari (BharSt_1.61, mṛga-mīna-sajjanānāṃ...)
  _AddArya(['LLGLGLGG', 'LLLLGGLLLLGGG', 'GLLGLLLLG', 'GGLLGLGLLL'])
  # From Bhartṛhari (BharSt_1.87, chinno 'pi rohati taruḥ...)
  _AddArya(['GGLGLLLG', 'GGLLGLGLGGL', 'LLLLGGGG', 'GGGGLGGL'])
  # From Bhartṛhari (BharSt_1.104, apriya-vacana-daridraiḥ...)
  _AddArya(['GLLLLLLGG', 'LLLLGGLGLLLGG', 'LLLLGLLGG', 'LGLGGLGLLG'])
  # From Bhartṛhari (BharSt_2.60, "kaś cumbati kula-puruṣo...")
  _AddArya(['GGLLLLLLG', 'GGLLGLGLGLLL', 'GLLLGLGLL', 'LLLLGGLLLGL'])
  # From Bhartṛhari ("virahe 'pi saṅgamaḥ khalu...", K48.328 (129))
  _AddArya(['LLGLGLGLL', 'LGLGGLGLGGG', 'LLLLLLLLGG', 'LGLLLGLGLLL'])
  # From Bhartṛhari ("sva-para-pratārako...", K48.120 (47))
  _AddArya(['LLGLGLGG', 'GLLGGLGLGLLG', 'GGLLGLLG', 'GGGGLGLLL'])
  # From Bhartṛhari ("prathitaḥ praṇayavatīnāṃ...", K48.274 (107))
  _AddArya(['LLGLLLLGG', 'GGLLGLGLLLGG', 'LLLLGGGLL', 'LLLLGLLLLLGL'])
  # From Bhartṛhari ("sahakāra-kusuma-kesara-...", K48.340 (132))
  _AddArya(['LLGLLLLGLL', 'LLLLGGLGLLLGG', 'LLLLLLLLLLG', 'LGLGGLGGG'])
  # From Bhartṛhari ("upari ghanaṃ...", K48.87 (34))
  _AddArya(['LLLLGLLLLG', 'GGLLGLGLLLGG', 'LLLLGLLLLG', 'GGLLGLGLLL'])
  # From Bhartṛhari ("yady asya..", K48.309 (121))
  _AddArya(['GGLGLLLG', 'GGGGLGLGGL', 'LLGGLLGG', 'LLGGGLGGG'])


def _PatternsOfLength(n):
  if n in _patterns_memo:
    return _patterns_memo[n]
  _patterns_memo[n] = [p + 'L' for p in _PatternsOfLength(n - 1)]
  _patterns_memo[n] += [p + 'G' for p in _PatternsOfLength(n - 2)]
  return _patterns_memo[n]
_patterns_memo = {0: [''], 1: ['L']}


def _AddAryaRegex():
  _AddMetreRegex('Āryā (matched from regex)',
                 ['|'.join(_PatternsOfLength(12)),
                  '|'.join([p + '[LG]' for p in _PatternsOfLength(16)]),
                  '|'.join(_PatternsOfLength(12)),
                  '|'.join([p + '[LG]' for p in _PatternsOfLength(13)])],
                 simple=False)


def _AddGiti(line_patterns):
  """Add an example of Gīti, with proper morae checking."""
  assert len(line_patterns) == 4
  expected = [12, 18, 12, 18]
  for i in range(4):
    allow_loose_ending = False
    if i % 2 and line_patterns[i].endswith('L'):
      allow_loose_ending = True
      expected[i] -= 1
    assert _MatraCount(line_patterns[i]) == expected[i], (
        i, line_patterns[i], _MatraCount(line_patterns[i]), expected[i])
    if allow_loose_ending:
      line_patterns[i] = line_patterns[i][:-1] + '.'
  # TODO(shreevatsa): Should we just add (up to) 4 patterns instead?
  _AddMetreRegex('Gīti', line_patterns, simple=False)


def _AddGitiExamples():
  # From Bhartṛhari (BharSt_2.26, āmīlitanayanānāṃ...)
  _AddGiti(['GGLLLLGG', 'GLLLLGLGLGGL', 'LLGLGLGLL', 'LLLLLLGLGLGLLL'])
  # The version of the above in Kosambi
  _AddGiti(['GGLLLLGG', 'GLLLLGLGLGLLG', 'LLGLGLGLL', 'GLLLLGLGLGLLG'])


def _AddKarambajati():
  """Examples of Upajāti of Vaṃśastham and Indravaṃśā."""
  # # Bhartṛhari
  # _AddSamavrttaPattern('Vaṃśastham (Vaṃśasthavila)',
  #                      'L G L G G L L G L G L G')
  # # Māgha
  # _AddSamavrttaPattern('Indravaṃśā', 'G G L G G L L G L G L G')
  # Also add all their Upajāti mixtures, with the above two 0000 and 1111
  # Allow final laghu
  # _AddSamavrttaRegex('Karambajāti (Vaṃśastham/Indravaṃśā)',
  #                   '. G L G G L L G L G L .')
  _AddSamavrttaRegex('Vaṃśastham/Indravaṃśā',
                     '. G L G G L L G L G L .')
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


_curated_vrtta_data = [
    # Bhartṛhari
    ('Upajāti', '. G L G G L L G L G .'),
    # Bhartṛhari
    ('Rathoddhatā', 'G L G L L L G L G L G'),
    # Bhāravi
    ('Svāgatā', 'G L G L L L G L L G G'),
    # Bhartṛhari
    ('Drutavilambitam', 'L L L G L L G L L G L G'),
    # Māgha
    ('Mañjubhāṣiṇī', 'L L G L G L L L G L G L G'),
    # Bhartṛhari
    ('Śālinī', 'G G G G — G L G G L G G'),
    # Bhāravi
    ('Praharṣiṇī', 'G G G L L L L G L G L G G'),
    # Bhāravi
    ('Pramitākṣarā', 'L L G L G L L L G L L G'),
    # Bhartṛhari
    # TODO(shreevatsa): pādānta-lagu whitelist: +Vasantatilakā, -Śālinī
    ('Vasantatilakā', 'G G L G L L L G L L G L G G'),
    # Bhartṛhari
    ('Mālinī', 'L L L L L L G G — G L G G L G G'),
    # Meghadūta
    ('Mandākrāntā', 'G G G G — L L L L L G — G L G G L G G'),
    # Bhartṛhari
    ('Śikhariṇī', 'L G G G G G – L L L L L G G — L L L G'),
    # Bhartṛhari
    ('Hariṇī', 'L L L L L G — G G G G — L G L L G L G'),
    # Bhartṛhari
    ('Pṛthvī', 'L G L L L G L G—L L L G L G G L G'),
    # Bhartṛhari
    ('Śārdūlavikrīḍitam',
     'G G G L L G L G L L L G — G G L G G L G'),
    # Bhartṛhari
    ('Sragdharā',
     'G G G G L G G — L L L L L L G — G L G G L G G'),
    # Bhartṛhari
    ('Viyoginī', ['L L G   L L G L G L G', 'L L G G L L G L G L G']),
    # Bhāravi
    ('Aupacchandasikam (Vasantamālikā) (Upodgatā)',
     ['L L G   L L G L G L G G', 'L L G G L L G L G L G G']),
    # Bhāravi
    ('Aparavaktrā', ['L L L L L L G — L G L G', 'L L L L G — L L G L G L G']),
    # Bhartṛhari
    ('Puṣpitāgrā', ['L L L L L L G L G L G G', 'L L L L G L L G L G L G G']),
    # Bhāravi
    ('Udgatā', ['L L  G  L  G  L L L G L',
                'L L L L L  G  L  G  L G',
                ' G  L L L L L L  G  L L G',
                'L L  G  L  G  L L L  G  L G L G']),
    # Bhartṛhari
    ('Dodhakam', 'G L L G L L G L L G G'),
    # Bhāravi
    ('Matta-mayūram', 'G G G G – G L L G G – L L G G'),
    # Bhāravi
    ('Kṣamā (Candrikā, Utpalinī)', 'LLLLLLGGLGGLG'),
    # Bhāravi
    ('Prabhā (Mandākinī)', 'LLLLLLGLGGLG'),
    # Bhāravi
    ('Jaladharamālā', 'GGGGLLLLGGGG'),
    # Bhāravi
    ('Jaloddhatagatiḥ', 'LGLLLGLGLLLG'),
    # Bhāravi
    ('Madhyakṣāmā (Haṃsaśyenī, Kuṭila, Cūḍāpīḍam)',
     'G G G G L L L L L L G G G G'),
    # Bhāravi
    ('Vaṃśapatrapatitam (Vaṃśadala)',
     'G L L G L G L L L G L L L L L L G'),
    # Māgha
    ('Rucirā (Prabhāvatī)', 'L G L G L L L L G L G L G'),
    # Raghuvamśa (hard to believe, but there it is)
    ('Nārācam', 'L L L L L L G L G G L G G L G G L G'),

    ('Bhujañgaprayātam', 'L G G L G G L G G L G G'),
    ('Toṭakam', 'L L G L L G L L G L L G'),
    ('Sragviṇī', 'G L G G L G G L G G L G'),
    ('Cārucāmaram', 'G L G L G L G L G L G L G L G'),
    ('Pañcacāmaram', 'L G L G L G L G L G L G L G L G'),
    ('Kokilalam (Nardaṭakam)', 'L L L L G L G L L L G — L L G L L G'),
    ('Mallikāmālā (Matta-kokilā)', 'G L G L L G L G L L G L G L L G L G'),
    ('Aśvadhāṭī (Sitastavaka?)',
     'G G L G L L L – G G L G L L L – G G L G L L L G'),
    ('Śivatāṇḍava',
     'L G L L  L G L L  L G L L  L G L L  L G L L  L G L L  L G'),
    # # AddMatravrtta('Pādākulakam (and many other names)', ['4 * 4'] * 4)
    ('Mālatī', 'L L L L G L L G L G L G'),
    ('Madīrā', 'G L L  G L L  G L L  G L L  G L L  G L L  G L L  G'),
    ('Vidyunmālā', 'G G G G G G G G'),
    ]


def InitializeData():
  """Add all known metres to the data structures."""
  _AddAnustup()
  _AddAnustupExamples()

  # AddMatravrtta('Āryā (mātrā)', [12, 18, 12, 15])
  _AddAryaExamples()
  _AddAryaRegex()
  _AddGitiExamples()

  _AddKarambajati()

  for (name, description) in _curated_vrtta_data:
    samatva = None
    need_regex = None
    if isinstance(description, list):
      assert len(description) in [2, 4]
      samatva = 'ardhasama' if len(description) == 2 else 'viṣama'
      need_regex = 'pattern'
    else:
      samatva = 'sama'
      if re.match(r'^[LG]*$', _RemoveChars(description, ' —–')):
        need_regex = 'pattern'
      else:
        need_regex = 'regex'

    assert samatva in ['sama', 'ardhasama', 'viṣama']
    assert need_regex in ['regex', 'pattern']

    if samatva == 'sama' and need_regex == 'regex':
      _AddSamavrttaRegex(name, description)
    elif samatva == 'sama' and need_regex == 'pattern':
      _AddSamavrttaPattern(name, description)
    elif samatva == 'ardhasama' and need_regex == 'pattern':
      _AddArdhasamavrttaPattern(name, description)
    elif samatva == 'viṣama' and need_regex == 'pattern':
      _AddVishamavrttaPattern(name, description)
    else:
      assert False, name
