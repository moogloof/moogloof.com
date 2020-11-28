from flask import render_template

from moogloof.app import app


@app.route("/")
def home():
	return render_template("home.html")

