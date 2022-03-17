# Package imports
from flask import Flask
from flaskext.markdown import Markdown

# App imports

# Create app
app = Flask(__name__)
app.config.from_pyfile("config.py")

md = Markdown(app, extensions=["fenced_code"])

# App functions
import moogloof.context_processors
import moogloof.views
import moogloof.chat_views

