# -*- coding: utf-8 -*-
"""Data structure that stores the result of a metre matching a known pattern."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from poor_enums import Enum

MATCH_TYPE = Enum(UNKNOWN=0,
                  # FULL=1,
                  # PADA=2,
                  # ODD_PADA=3,
                  # EVEN_PADA=4,
                  # # HALF=5,
                  # # FIRST_HALF=6,
                  # # SECOND_HALF=7,
                  # PADA_1=8,
                  # PADA_2=9,
                  # PADA_3=10,
                  # PADA_4=11
                 )


def Names(match_results):
  return ' AND '.join(m for m in match_results)


def Description(match_results, indent_depth=0):
  indent = ' ' * indent_depth
  s = ''
  for (i, result) in enumerate(match_results):
    s += indent + 'Result %d: ' % i
    s += '\n' + indent + '\tMetre name: %s' % result
    s += '\n'
  return s
