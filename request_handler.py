"""The web interface."""

from __future__ import absolute_import, division, print_function, unicode_literals

import webapp2
from google.appengine.ext.webapp import template

import identifier_pipeline
import views.identify
import views.main
import views.show_split


common_identifier = identifier_pipeline.IdentifierPipeline()


template.register_template_library('templates.filters')

# Handles all requests to sanskritmetres.appspot.com
application = webapp2.WSGIApplication([
    ('/', views.main.MainPage),
    webapp2.Route(r'/identify', handler=views.identify.IdentifyPage, defaults={'identifier':common_identifier}),
    ('/split', views.show_split.ShowBlocks),
    ('/statistics', views.main.StatsPage),
], debug=True)
