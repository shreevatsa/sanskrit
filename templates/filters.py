# -*- coding: utf-8 -*-

"""Some additional filters for our templates."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from google.appengine.ext.webapp import template

register = template.create_template_register() # pylint: disable=invalid-name

@register.filter
def pre_fixed(content):
  # # Hack: pre ignores first newline, so we add an additional one.
  # if content and content[0] == '\n':
  #   content = '\n' + content
  return content
