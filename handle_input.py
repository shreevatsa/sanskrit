"""Utils to clean up input."""

from __future__ import unicode_literals

import re

import simple_utils
import slp1
import transliterate


def CleanHK(text):
  """Transliterates text to SLP1, removing all other characters."""
  orig_text = text
  known_chars = " 0123456789'./$&%{}|-!"
  (text, rejects) = transliterate.Transliterate(
      transliterate.MakeStateMachine(transliterate.HKToSLP1Table()),
      text, pass_through=known_chars)
  if rejects:
    print 'Unknown characters are ignored:'
    print orig_text
    print ''.join('^' if i in rejects else ' ' for i in range(len(orig_text)))
  text = simple_utils.RemoveChars(text, known_chars)
  valid = slp1.VALID
  assert not re.search('[^%s]' % valid, text), text
  return text


def CleanLines(lines):
  cleaned_lines = []
  for line in lines:
    line = line.strip()
    if not line: continue
    line = CleanHK(line)
    cleaned_lines.append(line)
  return cleaned_lines
