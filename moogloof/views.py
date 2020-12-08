# Package imports
from datetime import datetime, timezone
from flask import render_template, session, redirect, url_for, request, abort, flash

# App imports
from moogloof.app import app
from moogloof.db import get_db
from moogloof.config import PASSWORD, LOGGED_ID


# Home page
@app.route("/")
def home():
	# Render the homepage template
	return render_template("home.html")

# Merch page
@app.route("/merch")
def merch():
	# Render merch template
	return render_template("merch.html", header="merch")

# Blog page
# Blog post page
@app.route("/blog")
@app.route("/blog/<title>")
def blog(title=None):
	# Get the post collection
	posts = get_db().moogloof.posts

	# Different handling depending on title
	if not title:
		# Get the entire list of posts sorted by date
		post_q = posts.find().sort("date", -1)

		# Render all posts
		return render_template("blog.html", header="blog", posts=post_q)
	else:
		# Get post with matching title
		post = posts.find_one({
			"title": title
		})

		if not post:
			# No post with title exists
			abort(404)
		else:
			# Render post
			return render_template("post.html", header="post", post=post)

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

# Login page
@app.route("/login", methods=["GET", "POST"])
def login():
	# Check if the form was submitted
	if request.method == "POST":
		# Get form password input
		password = request.form["password"]

		# Check if password is valid
		if password == PASSWORD:
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

