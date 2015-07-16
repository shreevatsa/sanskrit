# -*- coding: utf-8 -*-

"""Cleanup transformations: simple functions which take text and return text."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import Counter
from functools import wraps
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
  for line in text.split('\n'):
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
  control = Counter(c for c in text if unicodedata.category(c).startswith('C') and c != '\n')
  without_control = ''.join(c for c in text if c not in control)
  if text != without_control:
    logging.info('Removed control characters: %s', control)
  return without_control


def split_further_at_verse_numbers(verses):
  """Detect verses containing verse-end markers in them, and split them further."""
  new_verses = []
  for verse in verses:
    current_verse_lines = []
    lines = verse.split('\n')
    for line in lines:
      current_verse_lines.append(line)
      if len(current_verse_lines) in [2, 4] and remove_verse_numbers(line) != line:
        new_verses.append('\n'.join(current_verse_lines))
        current_verse_lines = []
    if current_verse_lines:
      new_verses.append('\n'.join(current_verse_lines))
  return new_verses


# Gretil-specific filters below this line
def after_second_comment_line(text):
  """Assuming text starts after second <!----...--><BR> line."""
  split = '<!---------------------------------------------------------><BR>\n'
  parts = text.split(split)
  if len(parts) == 3:
    return parts[2]
  logging.debug('Splitting at comment line gave %d parts.', len(parts))
  return text


def is_parenthesized_line(text):
  return bool(re.match(r'^[(].*[)] ?<BR>$', text))


def is_empty(text):
  return (re.match(r'^[ \t]*$', text) or text in ['<BR>', '***<BR>'] or
          re.match(r'^[_]{50,65}<BR>', text))


def _print_rejection(reason, if_different=False):
  """When one of our rejection functions below return True, print it."""
  def decorated(func):
    """Returns what the function will actually be after this decorator."""
    @wraps(func)
    def real(text, *args, **kwargs):
      """What the function will be, etc."""
      ret = func(text, *args, **kwargs)
      must_print = False
      if if_different:
        must_print = text != ret
      else:
        must_print = bool(ret)
      if must_print:
        print(('\nRejecting/changing verse (%s): {{{\n%s\n}}}\n' % (reason, text)).encode('utf-8'))
      return ret
    return real
  return decorated

# @_print_rejection(reason='starts with BR')
# def starts_with_br(text):
#   return text.startswith('<BR>')


def is_header_line(text):
  return bool(re.match(r'^Main Text<BR>$', text))


def is_footnote_line(text):
  return bool(re.match(r'^\\footnote{.*<BR>$', text))


def is_asterisked_variant_line(text):
  if re.match(r'^[*].*<BR>\n.*<BR>$', text):
    return True


def is_work_footer_line(text):
  return bool(re.match(r'^[ \t]*iti .*<BR>', text) or text == 'śrīrāmodantaṃ samāptam |<BR>')


def is_section_header_line(text):
  return bool(re.match(r'^\[[^ ]*\]<BR>', text))


def remove_leading_section_header_line(verse):
  lines = verse.split('\n')
  if re.match(r'^(&nbsp;){5}atha ', lines[0]) and remove_verse_numbers(lines[0]) != lines[0]:
    lines = lines[1:]
  return '\n'.join(lines)


def is_html_footer_line(text):
  return text == '</font></body></html>'


@_print_rejection(reason='edition info')
def is_edition_info(text):
  return text.startswith('This edition is based on') and text == remove_verse_numbers(text)


@_print_rejection(reason='parentheses info')
def is_parentheses_info(text):
  return (text.startswith('The parentheses in between verses contain') and
          text == remove_verse_numbers(text))


def is_footnote_followed_by_variant_line(text):
  lines = text.splitlines()
  return (len(lines) == 2 and is_footnote_line(lines[0]) and
          (is_parenthesized_line(lines[1]) or
           lines[1] == 'nāryo mugdhaśaṭhā haranti ramaṇaṃ tiṣṭhanti no vāritās<BR>'))


def clean_leading_br(text):
  lines = text.split('\n')
  if len(lines) == 5 and lines[0] == '... <BR>':
    return '\n'.join(lines[1:])
  else:
    return text


def clean_leading_parenthesized_line(text):
  lines = text.split('\n')
  if len(lines) == 5 and is_parenthesized_line(lines[0]):
    return '\n'.join(lines[1:])
  else:
    return text


def remove_trailing_parenthesized_line(verse):
  lines = verse.split('\n')
  if is_parenthesized_line(lines[-1]):
    lines = lines[:-1]
  return '\n'.join(lines)


def clean_leading_footnote(text):
  lines = text.split('\n')
  if len(lines) == 5 and is_footnote_line(lines[0]):
    return '\n'.join(lines[1:])
  else:
    return text


def is_verses_found_elsewhere_line(text):
  return bool(re.match(r'Verses found in .* not found here<BR>$', text))


def _is_abbreviation_line(line):
  """Lines like these:
su. = subhāṣitaratnakoṣa, <BR>
sad. = saduktikarṇāmṛta,<BR>
subh. = subhāṣitāvalī, <BR>
sū. = sūktimuktāvalī, <BR>
pad. = padyāvalī, <BR>
śā. = śārṅgadharapaddhati<BR>
  """
  return re.match(r'[^ \n]*\. = [^ \n]*(, )?<BR>$', line)


def is_abbreviation_block(text):
  lines = text.split('\n')
  return all(_is_abbreviation_line(line) for line in lines)


def split_verses_at_br(text):
  """Assume that <BR> by itself on a line is what separates verses."""
  lines = text.split('\n')
  verses = []
  current_verse_lines = []
  for line in lines:
    if line == '<BR>':
      if current_verse_lines:
        verses.append('\n'.join(current_verse_lines))
      current_verse_lines = []
    else:
      current_verse_lines.append(line)
  if current_verse_lines:
    verses.append('\n'.join(current_verse_lines))
  return verses


def is_text_abbreviation_header(verse):
  return verse in ['Text<BR>\nAbbreviations <BR>', 'Text<BR>\nābbreviations<BR>']


def is_trailing_work_name_junk(verse):
  return verse == '''amaruśatakam}<BR>
āmaruśatakam<BR>
amarukaviracitam}<BR>
āmarukaviracitam}}<BR>'''


@_print_rejection('variant line', if_different=True)
def remove_trailing_variant_line(verse):
  """If 2-line verse has a '*VAR' line appended, trim it."""
  lines = verse.split('\n')
  if len(lines) == 3 and re.match(r'^\*VAR.:?[ ]*(\{|[0-9]{1,2}b)', lines[2]):
    return '\n'.join(lines[:2])
  return verse


def is_work_header_line(verse):
  return verse == 'śrīrāmodantam |<BR>' or verse == 'Bhallaṭaśataka<BR>'
