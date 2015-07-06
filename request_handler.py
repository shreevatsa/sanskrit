"""The web interface."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cgi
import codecs

import webapp2
from google.appengine.ext.webapp import template

from data.metrical_data import HtmlDescription as MetreHtmlDescription
import simple_identifier
from transliteration import transliterate


def InputForm(default=''):
  return """
    <form action="/identify" method="post">
      <div>
        <textarea name="input_verse" rows="6" cols="80" autofocus>%s</textarea>
      </div>
      <div><input type="submit" value="Identify verse"></div>
    </form>""" % cgi.escape(default)


def StatsTable():
  return codecs.open('texts/gretil_stats/stats_table.html', 'r', 'utf-8').read()


def _DisplayName(metre_name):
  assert isinstance(metre_name, unicode)
  both_names = transliterate.AddDevanagariToIast(metre_name)
  return '<font size="+2">%s</font>' % both_names


common_identifier = simple_identifier.SimpleIdentifier()


class MainPage(webapp2.RequestHandler):

  def get(self):
    self.response.write(template.render('templates/main_page.html',
                                        {
                                          'INPUT_FORM': InputForm(),
                                          'METRE_STATISTICS' : StatsTable()
                                        }))


class IdentifyPage(webapp2.RequestHandler):

  def get(self):
    self.response.write(template.render('templates/main_page.html',
                                        {
                                          'INPUT_FORM': InputForm(),
                                          'METRE_STATISTICS' : StatsTable()
                                        }))

  def post(self):
    """What to do with the posted input string (verse)."""
    input_verse = self.request.get('input_verse')

    identifier = common_identifier
    identification = identifier.IdentifyFromLines(input_verse.split('\n'))

    full_match = None
    results = None
    first_result_display_name = None
    result_display_names = None
    if identification and identification[1]:
      (full_match, results) = identification
      if full_match:
        first_result_display_name = _DisplayName(results[0])
      else:
        result_display_names = []
        for m in results:
          result_display_names.append(_DisplayName(m))

    metre_blocks = []
    if identifier.tables:
      for (name, table) in identifier.tables:
        metre_block = {
          'metre_description' : MetreHtmlDescription(name),
          'metre_name': _DisplayName(name),
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
                            'input_form' : InputForm(input_verse),
                            'results': results,
                            'full_match': full_match,
                            'first_result_display_name': first_result_display_name,
                            'result_display_names': result_display_names,
                            'debug_read': identifier.DebugRead(),
                            'debug_identify': identifier.DebugIdentify(),
                            'metre_blocks': metre_blocks,
                            'bug_title': bug_title,
                            'bug_body': bug_body,
                          })
    self.response.write(out)


# Handles all requests to sanskritmetres.appspot.com
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/identify', IdentifyPage),
], debug=True)
