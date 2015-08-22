# -*- coding: utf-8 -*-

"""Identify."""

from __future__ import absolute_import, division, print_function, unicode_literals

from google.appengine.ext.webapp import template
import webapp2

class MainPage(webapp2.RequestHandler):
  """Handles requests to the main page."""
  def get(self):
    self.response.write(template.render('templates/main_page.html',
                                        {
                                            'default_identify_input': '',
                                        }))
