"""Utils for printing Unicode strings, lists, dicts, etc."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def ToUnicode(x):
  if isinstance(x, unicode):
    return x
  if isinstance(x, int):
    return unicode(x)
  if isinstance(x, list):
    return ListToUnicode(x)
  if isinstance(x, dict):
    return DictToUnicode(x)
  assert False, (x, type(x))


def ListToUnicode(li):
  assert isinstance(li, list)
  ret = ('[' + ', '.join(ToUnicode(i) for i in li) + ']')
  assert isinstance(ret, unicode)
  return ret


def DictToUnicode(d):
  assert isinstance(d, dict)
  ret = '{'.encode('utf-8')
  for (key, value) in sorted(d.items(), key=lambda x: x[1], reverse=True):
    ret += ('\n  ' + key + ': ' + ToUnicode(value)).encode('utf-8')
  ret += '\n}'.encode('utf-8')
  assert isinstance(ret, str)
  ret = ret.decode('utf-8')
  assert isinstance(ret, unicode)
  return ret


def Print(u):
  u = ToUnicode(u)
  assert isinstance(u, unicode), (u, type(u))
  print(u.encode('utf8'))

