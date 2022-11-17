# Package imports
from bson import json_util
from bson.objectid import ObjectId
from datetime import datetime, timezone
from flask import render_template, session, redirect, url_for, request, abort, flash, jsonify
from werkzeug.security import check_password_hash
import pymongo
import random

# App imports
from moogloof.app import app
from moogloof.db import get_db
from moogloof.config import PASSWORD, LOGGED_ID
from moogloof.context_processors import util_processor


# Home page
@app.route("/")
def home():
	random_phrases = ["Some sort of programmer. Can't figure out all those scary OS fanatics.", "Seven hundred seventy seven seventies have seventy seven seventy sevens.", "Years wasted watching anime. The mind degrades with each 300 chapter manga that is finished in one night.", "Struggling to learn x86 assembly.", "Building an OS called, idk loofOS.", "¡Me llame por la mañana para matarme!", "Really wants to travel to korea to meet with family.", "There is nothing more fulfilling in life than an interrupt handler that WORKS."]
	# Render the homepage template
	return render_template("home.html", random_phrase=random.choice(random_phrases))

# Merch page
@app.route("/merch")
def merch():
	# Render merch template
	return render_template("merch.html", header="merch")

# Blog page
# Blog post page
@app.route("/blog")
@app.route("/blog/<_id>")
def blog(_id=None):
	# Get the post collection
	posts = get_db().moogloof.posts

	# Different handling depending on title
	if not _id:
		# Get the entire list of posts sorted by date
		post_q = posts.find().sort("date", -1)[:3]

		# Render all posts
		return render_template("blog.html", header="blog", posts=post_q)
	else:
		# Get post with matching title
		post = posts.find_one({
			"_id": ObjectId(_id)
		})

		if not post:
			# No post with title exists
			abort(404)
		else:
			# Render post
			return render_template("post.html", header="post", post=post)

# Blog infinite scroll
@app.route("/blog/load")
def blog_load():
	# Get the post collection
	posts = get_db().moogloof.posts
	# Get the posts size
	post_size = posts.count()

	# Get load count
	count = int(request.args.get("c"))
	# Size of load
	load_size = 3

	# Loaded array
	loaded = []

	if not count * load_size > post_size:
		# Get loaded posts
		loaded = posts.find().sort("date", -1)[(count * load_size):((count + 1) * load_size)]

	timeago = util_processor()["timeago"]
	loaded = list(loaded)

	for d in loaded:
		d["date"] = timeago(d["date"])
		d["_id"] = str(d["_id"])

	response_data = json_util.dumps(loaded)

	# Return posts
	return app.response_class(response=response_data, status=200, mimetype='application/json')

# Create blog page
@app.route("/blog/create", methods=["GET", "POST"])
def create_blog():
	# Check if user is logged in
	if "logged-id" in session and session["logged-id"] == LOGGED_ID:
		# Saved is the form data to keep in case of invalid inputs
		saved = {}

		# Check if the form was submitted
		if request.method == "POST":
			# Clean the form
			post_title = request.form["title"].strip()
			post_content = request.form["content"]
			# Get the database
			db = get_db()

			# Make content saved to form
			saved["content"] = post_content

			# Validate post title
			if post_title == "":
				# Alert user that title cannot be whitespace
				flash("Your title can't just be whitespace bro.")
			elif bool(db.moogloof.posts.find_one({"title": post_title})):
				# Alert user that post with the same title already exists
				flash("Post with the same title exists.")
			else:
				# Create a new post
				new_post = {
					"date": datetime.now(timezone.utc),
					"title": post_title,
					"content": post_content
				}

				# Insert post into collection
				db.moogloof.posts.insert_one(new_post)

				# Redirect to the page of the post
				return redirect(url_for("blog", title=post_title))

		# Render the create page template
		return render_template("post_create.html", saved=saved)
	else:
		# Return with error if not logged in
		abort(403)

# Project page
@app.route("/projects")
def projects():
	# Get the projects
	projects = get_db().moogloof.projects.find()
	# Get updates
	updates = get_db().moogloof.updates

	# Get projects with 2 most recent udpates
	projects = list(map(lambda x: [x, updates.find({"project": x["_id"]}, limit=2, sort=[("date", pymongo.DESCENDING)])], projects))

	# Render projects
	return render_template("projects.html", header="projects", projects=projects)

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
	# Check if the form was submitted
	if request.method == "POST":
		# Get form password input
		password = request.form["password"]

		# Check if password is valid
		if check_password_hash(PASSWORD, password):
			# Login user
			session["logged-id"] = LOGGED_ID
			flash("Cool, you logged in.")

			# Redirect user to homepage
			return redirect(url_for("home"))
		else:
			# Alert user that password was incorrect
			flash("Nice try my guy.")

	# Render the login page template
	return render_template("login.html", header="login")

# Logout page
@app.route("/logout")
def logout():
	# Check if logged in
	if "logged-id" in session:
		# If logged in log out
		session.pop("logged-id")

	# Render the logout page template
	return render_template("logout.html", header="logout")

# Error 404 page
@app.errorhandler(404)
def page_not_found(e):
	# Render the 404 page template
	return render_template("404.html"), 404

# Error 403 page
@app.errorhandler(403)
def page_not_authorized(e):
	# Render the 403 page template
	return render_template("403.html"), 403

# Error 500 page
@app.errorhandler(500)
def server_error_page(e):
	# Render the 500 page template
	return render_template("500.html"), 500

