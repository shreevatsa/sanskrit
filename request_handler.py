"""The web interface."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import cgi
import codecs
import collections

import webapp2

import simple_identifier
import transliterate


def InputForm(default=''):
  return """
    <form action="/identify" method="post">
      <div><textarea name="input_verse" rows="6" cols="80">%s</textarea></div>
      <div><input type="submit" value="Identify verse"></div>
    </form>""" % cgi.escape(default)


def StatsTable():
  return codecs.open('gretil_stats/stats_table.html', 'r', 'utf-8').read()


def _UniqList(expr):
  return list(collections.OrderedDict.fromkeys(expr))


def _DisplayName(metre_name):
  metre_name = '%s' % metre_name
  return transliterate.AddDevanagariToIast(metre_name)


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
    results = identifier.IdentifyFromLines(input_verse.split('\n'))

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

    ok = False
    if results:
      assert isinstance(results, list)
      all_metres = _UniqList(m.MetreNameOnlyBase() for m in results)
      if len(all_metres) == 1:
        if len(results) == 1:
          ok = True
          self.response.write('<p>The metre is <font size="+2">%s</font>'
                              % _DisplayName(results[0]))
        else:
          self.response.write(
              '<p>The intended metre is probably <font size="+2">%s</font>' %
              _DisplayName(all_metres[0]))
      else:
        self.response.write('<p>The metre may be one of: %s.' %
                            ' OR '.join(_DisplayName(m) for m in all_metres))
    else:
      self.response.write('<p>No metre recognized.</p>')

    self.response.write('<hr/>')
    self.response.write('<p><i>Debugging output:</i></p>')
    self.response.write('<pre>')
    if not ok:
      pass
    self.response.write(identifier.AllDebugOutput())
    self.response.write('</pre>')
    self.response.write('\n')

    if identifier.tables:
      for (name, table) in identifier.tables:
        self.response.write('<p>Reading as %s:</p>' % _DisplayName(name))
        for line in table:
          self.response.write(line)
    self.response.write('</body></html>')


# Handles all requests to sanskritmetres.appspot.com
application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/identify', IdentifyPage),
], debug=True)
