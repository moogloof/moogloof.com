# Package imports
from flask import render_template

# App imports
from moogloof.app import app


# Chat dashboard page
@app.route("/", subdomain="chats")
def chats():
	return "bleh"

