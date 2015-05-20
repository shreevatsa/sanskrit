# -*- coding: utf-8 -*-
"""Data structure that stores the result of a metre matching a known pattern."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

def Description(match_results, indent_depth=0):
  indent = ' ' * indent_depth
  s = ''
  for (i, result) in enumerate(match_results):
    s += indent + 'Result %d: ' % i
    s += '\n' + indent + '\tMetre name: %s' % result
    s += '\n'
  return s
