"""The web interface."""

from flask import Flask

import identifier_pipeline

app = Flask(__name__)

# Register the custom template filter
@app.template_filter('pre_fixed')
def pre_fixed(content):
    return content

common_identifier = identifier_pipeline.IdentifierPipeline()

# Import and register route blueprints/views
import views.main
import views.identify
import views.show_split

app.add_url_rule('/', view_func=views.main.main_page)
app.add_url_rule('/identify', view_func=views.identify.identify_page, methods=['GET', 'POST'], defaults={'identifier': common_identifier})
app.add_url_rule('/split', view_func=views.show_split.show_blocks, methods=['GET', 'POST'])
app.add_url_rule('/statistics', view_func=views.main.stats_page)
app.add_url_rule('/fulltextAPI', view_func=views.main.fulltext_data, methods=['GET', 'POST'])
app.add_url_rule('/fulltext', view_func=views.main.fulltext_page)
app.add_url_rule('/alignmentAPI', view_func=views.main.alignment_api, methods=['POST'])

if __name__ == '__main__':
    app.run(debug=True)
