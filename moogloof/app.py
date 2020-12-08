# Package imports
from flask import Flask

# App imports
from moogloof.config import SECRET_KEY

# Create app
app = Flask(__name__)
app.secret_key = SECRET_KEY

# App functions
import moogloof.context_processors
import moogloof.views

