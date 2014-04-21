"""Align a verse to a given metre."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

_GAP_CHAR = '-'


def _Align(s, t):
  """Find best alignment of strings s and t."""
  m = len(s)
  n = len(t)
  addition_cost = 1           # Cost of adding an extra character in s
  deletion_cost = 1           # Cost of skipping a character of t
  def MismatchCost(i, j):
    """Cost of characters in s and t not matching."""
    return 0 if s[i - 1] == t[j - 1] else 1
  max_cost = m * n + 1
  best = [[max_cost] * (n + 1) for _ in range(m + 1)]
  best[0][0] = 0
  for i in range(m + 1):
    for j in range(n + 1):
      if i > 0: best[i][j] = min(best[i][j], best[i-1][j] + addition_cost)
      if j > 0: best[i][j] = min(best[i][j], best[i][j-1] + deletion_cost)
      if i > 0 and j > 0:
        best[i][j] = min(best[i][j], best[i-1][j-1] + MismatchCost(i, j))
  for j in range(1, n + 1):
    assert best[0][j] == deletion_cost * j
  for i in range(1, m + 1):
    assert best[i][0] == addition_cost * i
  # Now actually find the alignment
  i = m
  j = n
  aligned_s = ''
  aligned_t = ''
  while i > 0 or j > 0:
    if i > 0 and best[i][j] == best[i-1][j] + addition_cost:
      aligned_s += s[i - 1]
      aligned_t += _GAP_CHAR
      i -= 1
    elif j > 0 and best[i][j] == best[i][j-1] + deletion_cost:
      aligned_s += _GAP_CHAR
      aligned_t += t[j - 1]
      j -= 1
    else:
      assert i > 0 and j > 0
      assert best[i][j] == best[i-1][j-1] + MismatchCost(i, j)
      aligned_s += s[i - 1]
      aligned_t += t[j - 1]
      i -= 1
      j -= 1
  assert i == 0 and j == 0
  aligned_s = ''.join(reversed(aligned_s))
  aligned_t = ''.join(reversed(aligned_t))
  assert len(aligned_s) == len(aligned_t)
  return (aligned_s, aligned_t)


# Take verse_pattern too, because of additional display chars in display_verse
def AlignVerseToMetre(unused_display_verse, verse_pattern, metre_pattern_lines):
  """Match syllables of verse with those of metre."""
  metre_pattern = ''.join(metre_pattern_lines)
  (aligned_v, aligned_m) = _Align(verse_pattern, metre_pattern)

  assert len(aligned_v) == len(aligned_m)
  n = len(aligned_m)
  current_line = 0
  num_aligned = 0
  out = [[]]
  for i in range(n):
    out[-1].append((aligned_v[i], aligned_m[i]))
    num_aligned += (aligned_m[i] != _GAP_CHAR)
    if num_aligned == len(metre_pattern_lines[current_line]):
      current_line += 1
      num_aligned = 0
      out.append([])
  return out
