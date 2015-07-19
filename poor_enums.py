# -*- coding: utf-8 -*-
"""Poor man's enum, as AppEngine uses Python 2.7 (native enums are in 3.4+)."""

from __future__ import absolute_import, division, print_function, unicode_literals

def Enum(**enums):
  return type(str('Enum'), (), enums)
