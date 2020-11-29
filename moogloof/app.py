from flask import Flask

app = Flask(__name__)
app.secret_key = b'\t\xac+\x1a\x8e<*\xce\xac\x8e?"\xab\x12\xd8('

import moogloof.views

