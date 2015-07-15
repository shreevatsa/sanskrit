# -*- coding: utf-8 -*-

"""Cleanup transformations: simple functions which take text and return text."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re
import unicodedata


def process_crlf(text):
  """Removes occurences of the chr(13) character."""
  text = text.replace('\r\n', '\n')
  text = text.replace('\r', '\n')
  assert '\r' not in text
  return text


def process_html_line_breaks(text):
  """Turns <br> and <BR> into line breaks."""
  # Not using flags=re.IGNORECASE: <bR> <Br> rare, so prefer being conservative.
  text = text.replace('<BR>\n', '\n')
  text = text.replace('<br>\n', '\n')
  text = text.replace('<BR>', '\n')
  text = text.replace('<br>', '\n')
  return text


def process_html_spaces(text):
  """Replaces each &nbsp; with a space."""
  return text.replace('&nbsp;', ' ')


def process_html(text):
  """Runs two filters."""
  text = process_html_spaces(text)
  text = process_html_line_breaks(text)
  return text


def remove_verse_numbers(text):
  """Strips everything after ॥, ।।, // or || in each line."""
  # return re.subn(r'[/|]{2}[ \d.a-zA-z}_*\-]*[/|]{2}$', '', line)
  lines = []
  for line in text.splitlines():
    for marker in ['॥', '।।', '//', '||']:
      # If verse number was removed, can separate from next verse by blank line.
      (line, count) = re.subn(re.escape(marker) + '.*', '\n', line)
      # Don't expect text to have more than one verse-end marker. Break at first.
      if count:
        break
    lines.append(line)
  return '\n'.join(lines)


def debug_rejected_characters(orig_line, rejects):
  """Debug output about rejected characters, with their unicode codepoints and names."""
  def _unicode_notation(char):
    """The U+92ef etc. notation for a character."""
    assert isinstance(char, unicode)
    return '[U+%04x]' % ord(char)
  assert isinstance(orig_line, unicode)
  if not rejects:
    return
  line_read_as = ''.join(_unicode_notation(c) if c in rejects else c for c in orig_line)
  rejects = [(c, _unicode_notation(c), unicodedata.name(c, 'Unknown')) for c in rejects]
  rejects = ', '.join('%s (%s %s)' % reject for reject in rejects)
  logging.debug('Unknown characters are ignored: %s\nin line:\n%s', rejects, line_read_as)


def normalize_nfkc(text):
  """Normalize text to NFKC."""
  nfkc = unicodedata.normalize('NFKC', text)
  if text != nfkc:
    logging.debug('%s normalized to %s', text, nfkc)
  if nfkc != unicodedata.normalize('NFC', text):
    logging.warning('NFC and NFKC normalizations differ for %s', text)
  return nfkc


def remove_control_characters(text):
  """Remove non-printable (control) characters in text, and warn."""
  text = text.replace('\t', ' ')  # a tab is a control character too
  control = set(c for c in text if unicodedata.category(c).startswith('C') and c != '\n')
  without_control = ''.join(c for c in text if c not in control)
  if text != without_control:
    logging.info('''Removed control characters %s in ```\n%s```
    to get ```\n%s```''', control, text, without_control)
  return without_control


def after_second_comment_line(text):
  """Assuming text starts after second <!----...--><BR> line."""
  split = '<!---------------------------------------------------------><BR>\n'
  parts = text.split(split)
  if len(parts) == 3:
    return parts[2]
  logging.debug('Splitting at comment line gave %d parts.', len(parts))
  return text
