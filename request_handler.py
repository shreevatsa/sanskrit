"""The class that actually handles the input verse."""

import cgi
import StringIO

import webapp2

import sscan

MAIN_PAGE_HTML = """\
<html>
  <body>
    <form action="/identify" method="post">
      <div><textarea name="input_verse" rows="6" cols="80"></textarea></div>
      <div><input type="submit" value="Identify verse"></div>
    </form>
  </body>
</html>
"""


class InputPage(webapp2.RequestHandler):
  def get(self):
    self.response.write(MAIN_PAGE_HTML)


class IdentifyPage(webapp2.RequestHandler):
  def post(self):
    self.response.write('<html><body>You wrote:<pre>')
    input_verse = self.request.get('input_verse')
    self.response.write(cgi.escape(input_verse))
    # TODO(shreevatsa): Ridiculous that this runs each time; needs fixing (easy)
    sscan.InitializeData()
    metre = sscan.IdentifyFromLines(input_verse.split('\n'))
    self.response.write(metre)
    self.response.write('</pre></body></html>')


application = webapp2.WSGIApplication([
    ('/', InputPage),
    ('/identify', IdentifyPage),
], debug=True)
