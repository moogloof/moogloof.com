from flask import render_template

from moogloof.app import app


@app.route("/")
def home():
	return render_template("home.html")

@app.route("/merch")
def merch():
	return render_template("merch.html", header="merch")

