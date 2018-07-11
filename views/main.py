# -*- coding: utf-8 -*-

"""Identify."""

from __future__ import absolute_import, division, print_function, unicode_literals

from google.appengine.ext.webapp import template
import webapp2
import json

from texts.read_gretil import metres_for_text, find_alignment
from print_utils import Print

class MainPage(webapp2.RequestHandler):
  """Handles requests to the main page."""
  def get(self):
    self.response.write(template.render('templates/main_page.html',
                                        {
                                            'default_identify_input': '',
                                        }))

class StatsPage(webapp2.RequestHandler):
  def get(self):
    self.response.write(template.render('templates/statistics.html', {}))

class FullTextData(webapp2.RequestHandler):
  def get(self):
      self.response.write('Please POST (with parameter fulltext).')
  def post(self):
      text = self.request.get('fulltext')
      print(self.request.__dict__)
      dummy_args = {
          'print_unidentified_verses': 'brief',
          'print_identified_verses': 'brief',
          'break_at_error': None,
      }
      ret = metres_for_text(text, dummy_args, custom_splitter=None)
      self.response.content_type = b'application/json'
      self.response.write(json.dumps(ret))

class FullTextPage(webapp2.RequestHandler):
  def get(self):
      self.response.write(template.render('templates/fulltext.html', {}))

class AlignmentAPI(webapp2.RequestHandler):
  def post(self):
      verse_text = self.request.get('verse_text')
      assert type(verse_text) == type('unicode literal')
      metre_name = self.request.get('metre_name')
      Print('Type of metre_name is ' + ('bytes' if type(metre_name) else 'unicode'))
      Print(type(metre_name))
      if isinstance(metre_name, bytes):
          metre_name = metre_name.decode('utf-8')
      print('Type of metre_name is ', type(metre_name))
      (alignment, table) = find_alignment(verse_text, metre_name)
      ret = {'alignment': alignment, 'table': table}
      self.response.content_type = b'application/json'
      self.response.write(json.dumps(ret))
      
