# Package imports
from flask import Flask

# App imports

# Create app
app = Flask(__name__)
app.config.from_pyfile("config.py")

# App functions
import moogloof.context_processors
import moogloof.views
import moogloof.chat_views

