"""The web interface."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cgi
import codecs
import collections

import webapp2

from data import metrical_data
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
  return codecs.open('gretil_stats/stats_table.html', 'r', 'utf-8').read()


def _UniqList(expr):
  return list(collections.OrderedDict.fromkeys(expr))


def _DisplayName(metre_name):
  assert isinstance(metre_name, unicode)
  both_names = transliterate.AddDevanagariToIast(metre_name)
  return '<font size="+2">%s</font>' % both_names


MAIN_PAGE_HTML = open('main_page_template.html').read()
MAIN_PAGE_HTML = MAIN_PAGE_HTML.replace('${INPUT_FORM}', InputForm())
MAIN_PAGE_HTML = MAIN_PAGE_HTML.replace('${METRE_STATISTICS}', StatsTable())


common_identifier = simple_identifier.SimpleIdentifier()


class MainPage(webapp2.RequestHandler):

  def get(self):
    self.response.write(MAIN_PAGE_HTML)


class IdentifyPage(webapp2.RequestHandler):

  def get(self):
    self.response.write(MAIN_PAGE_HTML)

  def post(self):
    """What to do with the posted input string (verse)."""
    input_verse = self.request.get('input_verse')

    identifier = common_identifier
    identification = identifier.IdentifyFromLines(input_verse.split('\n'))

    self.response.write('<html>\n')
    self.response.write('<head><style>\n')
    self.response.write('abbr {border-bottom: 1px dotted black; color:red;}\n')
    self.response.write('.sylL { } \n')
    self.response.write('.sylG { font-weight:bold; } \n')
    self.response.write('.syl- { } \n')
    self.response.write('</style></head>\n')

    self.response.write('<body>\n')
    self.response.write('<p>')
    self.response.write(InputForm(input_verse))
    self.response.write('</p>')

    if identification and identification[1]:
      (full_match, results) = identification
      self.response.write('<p>')
      if full_match:
        self.response.write('The metre is: ')
        self.response.write('%s.' % _DisplayName(results[0]))
      else:
        self.response.write('The input does not perfectly match '
                            'any known metre. </p>'
                            '<p>Based on partial matches, it may be:</p>')
        self.response.write('<ul>')
        for m in results:
          self.response.write('<li>%s</li>' % _DisplayName(m))
        self.response.write('</ul>')
    else:
      self.response.write('<p>No metre recognized.</p>')

    self.response.write('\n'.join(['<hr/>',
                                   '<p><i>Debugging output:</i></p>',
                                   '<details>',
                                   '<summary>Reading the input</summary>',
                                   '<pre>',
                                   identifier.DebugRead(),
                                   '</pre>',
                                   '</details>',
                                   '<details>',
                                   '<summary>Identifying the metre</summary>',
                                   '<pre>',
                                   identifier.DebugIdentify(),
                                   '</pre>',
                                   '</details>']))
    self.response.write('\n')

    if identifier.tables:
      self.response.write('<hr/><h2>About the results</h2>')
      for (name, table) in identifier.tables:
        self.response.write('<p>' + metrical_data.HtmlDescription(name))
        if not full_match:
          self.response.write('<p>The input verse imperfectly matches %s '
                              '(note deviations in red):</p>'
                              % _DisplayName(name))
        else:
          self.response.write('<p>The input verse matches %s:</p>'
                              % _DisplayName(name))
        for line in table:
          self.response.write(line)
    self.response.write('</body></html>')


# Handles all requests to sanskritmetres.appspot.com
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/identify', IdentifyPage),
], debug=True)
