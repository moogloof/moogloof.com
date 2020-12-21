# Package imports
from flask import Flask

# App imports
from moogloof.config import SECRET_KEY, SERVER_NAME

# Create app
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["SERVER_NAME"] = SERVER_NAME

# App functions
import moogloof.context_processors
import moogloof.views
import moogloof.chat_views

