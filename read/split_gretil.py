# -*- coding: utf-8 -*-

"""Split a GRETIL htm file into separate verses."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

# from print_utils import Print
import read.filters

def mss_splitter(text):
  """Split by matching MSS-* id."""
  verses = []
  lines_of_current_verse = []
  last_seen_verse_id = None
  ok_lines = [line for line in text.split('\n')
              if not read.filters.is_html_footer_line(line)]
  for line in ok_lines:
    if line == '<BR>' or line == '':
      assert (lines_of_current_verse == [] or
              lines_of_current_verse[0].startswith('MSS_9979-1'))
      continue
    match = re.match(r'^MSS_([0-9ABCD\-]+)-[1-5]', line)
    assert match, (line, 'line is #%s#' % line)
    current_verse_id = match.group(1)
    # line = line[len(match.group(0)):]
    if current_verse_id == last_seen_verse_id:
      lines_of_current_verse.append(line)
    else:
      if lines_of_current_verse:
        verses.append('\n'.join(lines_of_current_verse))
      last_seen_verse_id = current_verse_id
      lines_of_current_verse = [line]
  if lines_of_current_verse:
    verses.append('\n'.join(lines_of_current_verse))
  return verses


def split(text, custom_splitter=None):
  """Split text into separate verses."""
  text = read.filters.process_crlf(text)
  text = read.filters.normalize_nfkc(text)
  text = read.filters.remove_control_characters(text)

  text = read.filters.after_second_comment_line(text)

  if custom_splitter:
    return (custom_splitter(text), text)

  verses = read.filters.split_verses_at_br(text)

  verses = map(read.filters.remove_trailing_parenthesized_line, verses)
  verses = map(read.filters.clean_leading_footnote, verses)
  verses = map(read.filters.remove_trailing_variant_line, verses)
  verses = map(read.filters.remove_leading_section_header_line, verses)

  verses = map(read.filters.process_html_spaces, verses)

  # Tracer()()

  verses = read.filters.split_further_at_verse_numbers(verses)

  verses = [verse.strip('\n') for verse in verses]
  verses = [verse for verse in verses if
            not read.filters.is_parenthesized_line(verse) and
            not read.filters.is_empty(verse) and
            not read.filters.is_header_line(verse) and
            not read.filters.is_footnote_line(verse) and
            not read.filters.is_asterisked_variant_line(verse) and
            not read.filters.is_footnote_followed_by_variant_line(verse) and
            not read.filters.is_html_footer_line(verse) and
            not read.filters.is_verses_found_elsewhere_line(verse) and
            # not read.filters.starts_with_br(verse) and
            not read.filters.is_edition_info(verse) and
            not read.filters.is_text_abbreviation_header(verse) and
            not read.filters.is_parentheses_info(verse) and
            not read.filters.is_trailing_work_name_junk(verse) and
            not read.filters.is_section_header_line(verse) and
            not read.filters.is_work_footer_line(verse) and
            not read.filters.is_work_header_line(verse) and
            not read.filters.is_abbreviation_block(verse)]

  verses = map(read.filters.clean_leading_br, verses)
  verses = map(read.filters.clean_leading_parenthesized_line, verses)

  # Print('These are verses:')
  # for (i, verse) in enumerate(verses):
  #   # # Two or four lines
  #   # if (not re.match(r'^(.*<BR>\n){3}.*<BR>$', verse) and
  #   #     not re.match(r'^.*<BR>\n.*<BR>$', verse)):
  #     Print('\nVerse %d is:' % (i + 1))
  #     Print('\n    '.join(('    ' + verse).splitlines()))
  #     Print('End Verse %d\n' % (i + 1))

  return (verses, text)


# Hacky enum :-)
_DONT_HIGHLIGHT = False
_HIGHLIGHT = True

def find_verse_in_text(verse, text):
  """Yields (blocks, consumed) where blocks are (text_fragment, should_highlight),
  and consumed is the number of characters consumed in text."""
  # Print('Trying to find verse %s in text of length %d' % (verse, len(text)))
  words = re.split(r'(\s+)', verse)
  for word in words:
    assert word in text, (text, verse, word)
    where = text.find(word)
    yield (text[:where], _DONT_HIGHLIGHT)
    assert text[where : where + len(word)] == word
    # Print('Yielding found word: %s, %s' % (word, _HIGHLIGHT))
    yield (word, _HIGHLIGHT)
    text = text[where + len(word):]


def individual_blocks_of_verses_in_text(verses, text):
  """Splits text into blocks of text; each block is (text, should_highlight)."""
  while verses:
    verse = verses.pop(0)
    consumed = 0
    for block in find_verse_in_text(verse, text):
      consumed += len(block[0])
      yield block
    text = text[consumed:]
  if text:
    # Print('Leftover text after all verses: %s' % text)
    yield (text, _DONT_HIGHLIGHT)


def blocks_of_verses_in_text(verses, text):
  """Splits text into blocks of selected and not selected."""
  current_block = ('', None)
  for block in individual_blocks_of_verses_in_text(verses, text):
    if block[0] == '':
      continue
    if block[1] == current_block[1]:
      current_block = (current_block[0] + block[0], block[1])
    else:
      if current_block[0]:
        yield current_block
      current_block = block
  if current_block[0]:
    yield current_block
