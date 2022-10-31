#!/usr/bin/env python3
import os
from flask import Flask, redirect, request, url_for
import logging
import sys

logging.basicConfig(stream=sys.stdout, format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

signatures = []

app = Flask(__name__)

# configurations
font = os.environ.get('DISPLAY_FONT')
font_color = os.environ.get('DISPLAY_COLOR')
environment = os.environ.get('ENVIRONMENT')


@app.route('/', methods=['GET'])
def index():
    html = """
    Signatures: <br />
    <font face="%(font)s" color="%(color)s">
        %(messages)s
    </font>

    <br /> <br />
    <form action="/signatures" method="post">
        Sign the Guestbook: <input type="text" name="message"><br>
        <input type="submit" value="Sign">
    </form>

    <br />
    <br />
    Debug Info: <br />
    ENVIRONMENT is %(environment)s
    """
    messages_html = "<br />".join(signatures)
    return html % {"font": font, "color": font_color, "messages": messages_html, "environment": environment}

@app.route('/signatures', methods=['POST'])
def write():
    message = request.form.get('message')
    signatures.append(message)

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
