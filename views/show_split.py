"""Show the original text and how it was split into verses.

The assumption is that each word in each verse occurs as a contiguous word in the original text.
"""

import logging
from urllib.request import urlopen

from flask import render_template, request

import read.split_gretil


def show_blocks():
    if request.method == 'GET':
        return render_template('split.html')

    # POST: either a file is uploaded or a url
    action = request.form.get('submit_action')
    assert action in ['Upload', 'Retrieve'], action
    if action == 'Upload':
        uploaded_file = request.files.get('uploaded_htm_file')
        text = uploaded_file.read().decode('utf8', 'replace')
    else:
        try:
            url = request.form.get('url_of_htm_file')
            text = urlopen(url).read().decode('utf8')
        except Exception as error:
            logging.error(error)
            return render_template('split.html')

    if not text:
        return render_template('split.html')

    (verses, text) = read.split_gretil.split(text)
    blocks = list(read.split_gretil.blocks_of_verses_in_text(verses, text))

    return render_template('split.html', blocks=blocks)
