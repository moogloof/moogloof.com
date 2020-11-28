from flask import render_template

from moogloof.app import app
from moogloof.db import posts


@app.route("/")
def home():
	return render_template("home.html")

@app.route("/merch")
def merch():
	return render_template("merch.html", header="merch")

@app.route("/blog")
@app.route("/blog/<title>")
def blog(title=None):
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

