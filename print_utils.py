"""Utils for printing Unicode strings, lists, dicts, etc."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def ToUnicode(x):
  """Convert x to unicode, whatever it is."""
  if isinstance(x, unicode):
    return x
  if isinstance(x, int):
    return unicode(x)
  if isinstance(x, list):
    return _ListToUnicode(x)
  if isinstance(x, dict):
    return _DictToUnicode(x)
  # For MatchResult, use x.Name()
  if callable(getattr(x, 'Name', None)):
    return x.Name()
  assert False, (x, type(x))


def _ListToUnicode(li):
  assert isinstance(li, list)
  ret = '[%s]' % ', '.join(ToUnicode(i) for i in li)
  assert isinstance(ret, unicode)
  return ret


def _DictToUnicode(d):
  assert isinstance(d, dict)
  ret = '{'
  for (key, value) in sorted(d.items(), key=lambda x: x[1], reverse=True):
    ret += '\n  %s: %s' % (ToUnicode(key), ToUnicode(value))
  ret += '\n}'
  assert isinstance(ret, unicode)
  return ret


def Print(u):
  u = ToUnicode(u)
  assert isinstance(u, unicode), (u, type(u))
  print(u.encode('utf8'))
