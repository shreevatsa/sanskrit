import itertools
import subprocess
import sys

lines = [l.strip() for l in sys.stdin.readlines()]
for key, group in itertools.groupby(lines, bool):
  if not key:
    continue
  verse_lines = list(group)
  if verse_lines == ['{UttarameghaH}']:
    continue
  assert len(verse_lines) == 4, verse_lines
  subprocess.call('echo; echo "%s" | python sscan.py' % '\n'.join(verse_lines),
                  shell=True)
  
  
  
