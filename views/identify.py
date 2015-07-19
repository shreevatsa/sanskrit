# -*- coding: utf-8 -*-

"""Identify."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from google.appengine.ext.webapp import template
import webapp2

from data.metrical_data import HtmlDescription as MetreHtmlDescription
from transliteration import transliterate

def _display_name(metre_name):
  assert isinstance(metre_name, unicode)
  both_names = transliterate.AddDevanagariToIast(metre_name)
  return '<font size="+2">%s</font>' % both_names


class IdentifyPage(webapp2.RequestHandler):
  """The identify page."""
  def get(self, *dummy_args, **dummy_kwargs):
    self.response.write(template.render('templates/main_page.html',
                                        {
                                            'default_identify_input': 'satyameva jayate',
                                        }))

  def post(self, identifier=None):
    """What to do with the posted input string (verse)."""
    input_verse = self.request.get('input_verse')

    identification = identifier.IdentifyFromLines(input_verse.split('\n'))

    full_match = None
    results = None
    result_display_names = None
    if identification and identification[1]:
      (full_match, results) = identification
      result_display_names = [_display_name(m) for m in results]

    metre_blocks = []
    if identifier.tables:
      for (name, table) in identifier.tables:
        metre_block = {
            'metre_description' : MetreHtmlDescription(name),
            'metre_name': _display_name(name),
            'block': table,
        }
        metre_blocks.append(metre_block)


    bug_title = 'User feedback'
    bug_body = '''
I have an issue to report about the results for the following input:
```
%s
```

The issue is:
[Please input the issue here]
''' % input_verse
    out = template.render('templates/results.html',
                          {
                              'default_identify_input' : input_verse,
                              'results': results,
                              'full_match': full_match,
                              'first_result_display_name': result_display_names[0],
                              'result_display_names': result_display_names,
                              'debug_read': identifier.DebugRead(),
                              'debug_identify': identifier.DebugIdentify(),
                              'metre_blocks': metre_blocks,
                              'bug_title': bug_title,
                              'bug_body': bug_body,
                          })
    self.response.write(out)
