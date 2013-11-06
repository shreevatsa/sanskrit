from __future__ import unicode_literals

import re
import sys

import handle_input
import sscan

def RemoveHTML(text):
  return re.sub('<BR>', '', text)


def RemoveVerseNumber(text):
  return re.sub('//[ \d.a}]*//$', '', text)


if __name__ == '__main__':
  lines = []
  seen_separators = 0
  for l in sys.stdin.readlines():
    l = l.decode('utf8')
    l = RemoveHTML(l)
    l = l.strip()
    if seen_separators < 2 and re.search('<![-]{50,}->', l):
      seen_separators += 1
    elif seen_separators == 2 and not l.startswith('<'):
      lines.append(l)

  verses = handle_input.BreakIntoVerses(lines)
  for verse in verses:
    print '\n\t\t\t\t\t\t'.join([''] + verse)
    verse = [RemoveVerseNumber(l).strip() for l in verse]
    sscan.IdentifyFromLines(verse)
    print
