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
		saved = {}

		if request.method == "POST":
			post_title = request.form["title"].strip()
			post_content = request.form["content"]
			db = get_db()



			if post_title == "":
				flash("Your title can't just be whitespace bro.")
			elif bool(db.moogloof.posts.find_one({"title": post_title})):
				flash("Post with the same title exists.")
				saved["content"] = post_content
			else:
				new_post = {
					"date": datetime.now(timezone.utc),
					"title": post_title,
					"content": post_content
				}

				db.moogloof.posts.insert_one(new_post)

				return redirect(url_for("blog", title=post_title))

		return render_template("post_create.html", saved=saved)
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
	if "logged-id" in session:
		session.pop("logged-id")

	return render_template("logout.html", header="logout")

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(403)
def page_not_authorized(e):
	return render_template("403.html"), 403

