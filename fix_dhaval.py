"""New format for https://www.dropbox.com/s/gwc3lyqbj5frjw7/chhandascode.txt."""

import re
import sys

lines = sys.stdin.readlines()
for line in lines:
  assert line[-1] == '\n'
  line = line[:-1]
  prefix1 = 'AddSamavrtta'
  prefix2 = 'AddArdhasamavrtta'
  prefix3 = 'AddVishamavrtta'
  if re.match(prefix1, line):
    m = re.match(prefix1 + r"\('(?P<name>.*)', '(?P<line>.*)'\)", line)
    assert m
    name = m.group('name')
    assert name == name.strip()
    each = m.group('line').strip()
    line = "('%s', '%s')," % (name, each)
  elif re.match(prefix2, line):
    m = re.match(prefix2 +
                 r"\('(?P<name>.*)', '(?P<first>.*)', '(?P<second>.*)'\)", line)
    assert m
    name = m.group('name')
    assert name == name.strip()
    odd = m.group('first').strip()
    even = m.group('second').strip()
    line = "('%s', ['%s', '%s'])," % (name, odd, even)
  else:
    assert re.match(prefix3, line)
    m = re.match(prefix3 + r"\('(?P<name>.*)', '(?P<line1>.*)', '(?P<line2>.*)', '(?P<line3>.*)', '(?P<line4>.*)'\)", line)
    assert m
    name = m.group('name')
    assert name == name.strip()
    line = "('%s', ['%s', '%s', '%s', '%s'])," % (name, m.group('line1'),
                                                  m.group('line2'),
                                                  m.group('line3'),
                                                  m.group('line4'))
  print line
