"""Views for the main page, statistics, fulltext, and alignment API."""

import json

from flask import render_template, request

from texts.read_gretil import metres_for_text, find_alignment
from print_utils import Print


def main_page():
    return render_template('main_page.html', default_identify_input='')


def stats_page():
    return render_template('statistics.html')


def fulltext_data():
    if request.method == 'GET':
        return 'Please POST (with parameter fulltext).'
    text = request.form.get('fulltext', '')
    dummy_args = {
        'print_unidentified_verses': 'brief',
        'print_identified_verses': 'brief',
        'break_at_error': None,
    }
    ret = metres_for_text(text, dummy_args, custom_splitter=None)
    return json.dumps(ret), 200, {'Content-Type': 'application/json'}


def fulltext_page():
    return render_template('fulltext.html')


def alignment_api():
    verse_text = request.form.get('verse_text', '')
    metre_name = request.form.get('metre_name', '')
    (alignment, table) = find_alignment(verse_text, metre_name)
    ret = {'alignment': alignment, 'table': table}
    return json.dumps(ret), 200, {'Content-Type': 'application/json'}
