# -*- coding: utf-8 -*-
"""Poor man's enum, as AppEngine uses Python 2.7 (native enums are in 3.4+)."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def Enum(**enums):
  return type(str('Enum'), (), enums)

