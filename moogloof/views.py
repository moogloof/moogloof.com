from datetime import datetime, timezone
from flask import render_template, session, redirect, url_for, request, abort, flash

from moogloof.app import app
from moogloof.db import get_db
from moogloof.config import PASSWORD, LOGGED_ID


@app.route("/")
def home():
	return render_template("home.html")

@app.route("/merch")
def merch():
	return render_template("merch.html", header="merch")

@app.route("/blog")
@app.route("/blog/<title>")
def blog(title=None):
	posts = get_db().moogloof.posts

	if not title:
		post_q = posts.find().sort("date", -1)

		# Render all posts
		return render_template("blog.html", header="blog", posts=post_q)
	else:
		post = posts.find_one({
			"title": title
		})

		# Render post
		return render_template("post.html", header="post", post=post)

@app.route("/blog/create", methods=["GET", "POST"])
def create_blog():
	if "logged-id" in session and session["logged-id"] == LOGGED_ID:
		if request.method == "POST":
			new_post = {
				"date": datetime.now(timezone.utc),
				"title": request.form["title"],
				"content": request.form["content"]
			}

			get_db().moogloof.posts.insert_one(new_post)

			return redirect(url_for("blog", title=request.form["title"]))

		return render_template("post_create.html")
	else:
		abort(403)

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		password = request.form["password"]

		if password == PASSWORD:
			session["logged-id"] = LOGGED_ID
			flash("Cool, you logged in.")

			return redirect(url_for("home"))
		else:
			flash("Nice try my guy.")

	return render_template("login.html", header="login")

@app.route("/logout")
def logout():
	session.pop("logged-id")

	return render_template("logout.html", header="logout")

