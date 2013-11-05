"""Utils to clean up input."""

from __future__ import unicode_literals

import re

import simple_utils
import slp1
import transliteration_data


def TransliterateAndClean(text):
  """Transliterates text to SLP1, removing all other characters."""
  orig_text = text
  known_chars = " 0123456789'./$&%{}|-!"
  (text, rejects) = transliteration_data.DetectAndTransliterate(text)

  underline = ''
  if rejects:
    for i in range(len(orig_text)):
      if i in rejects and orig_text[i] not in known_chars:
        underline += '^'
      else:
        underline += ' '
  if underline.strip():
    print 'Unknown characters are ignored:'
    print orig_text
    print underline

  assert not re.search('[^%s]' % slp1.ALPHABET, text), text
  return text


def CleanLines(lines):
  cleaned_lines = []
  for line in lines:
    line = line.strip()
    if not line: continue
    line = TransliterateAndClean(line)
    cleaned_lines.append(line)
  return cleaned_lines
