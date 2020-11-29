from flask import Flask

from moogloof.config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

import moogloof.commands
import moogloof.views

