# Package imports
from bson import json_util
from bson.objectid import ObjectId
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from flask import render_template, session, redirect, url_for, request, abort, flash, jsonify
from werkzeug.security import check_password_hash
from bson.errors import InvalidId
import pymongo
import random
import requests

# App imports
from moogloof.app import app
from moogloof.db import get_db
from moogloof.config import PASSWORD, LOGGED_ID
from moogloof.context_processors import util_processor


# Home page
@app.route("/")
def home():
	random_phrases = ["Some sort of programmer. OS development is more fun than it looks.", "Euler invented a crazy amount of laws.", "loofOS, 2 years in the making.", "Struggling but nevertheless learning x86 assembly.", "Building an OS called, idk loofOS.", "Microkernels seem really neat until you have to implement a bootloader for one.", "Really wants to travel to korea to meet with family.", "There is nothing better than a long walk at night with friends."]
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
	# Get db
	db = get_db()

	# Different handling depending on title
	if not _id:
		# Get the entire list of posts sorted by date
		post_q = db.moogloof.posts.find().sort("date", -1)[:3]

		# Render all posts
		return render_template("blog.html", header="blog", posts=post_q)
	else:
		# Get post with matching title
		try:
			post = db.moogloof.posts.find_one({
				"_id": ObjectId(_id)
			})
		except InvalidId:
			abort(404)

		if not post:
			# No post with title exists
			abort(404)
		else:
			# Get comments corresponding to post
			comments_q = db.moogloof.comments.find({"post": ObjectId(_id)}, sort=[("date", pymongo.ASCENDING)])

			# Render post
			return render_template("post.html", header=post["title"], post=post, comments=comments_q)

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
		loaded = posts.find().sort("date", -1).skip(count * load_size).limit(load_size)

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
			post_thumb = request.form["thumbnail"].strip()
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

				# Add a thumbnail if specified
				if post_thumb:
					new_post["thumbnail"] = post_thumb

				# Insert post into collection
				inserted_post = db.moogloof.posts.insert_one(new_post)

				# Redirect to the page of the post
				return redirect(url_for("blog", _id=inserted_post.inserted_id))

		# Render the create page template
		return render_template("post_create.html", saved=saved)
	else:
		# Return with error if not logged in
		abort(403)

# Edit blog page
@app.route("/blog/<_id>/update", methods=["GET", "POST"])
def edit_blog(_id):
	# Check if user is logged in
	if "logged-id" in session and session["logged-id"] == LOGGED_ID:
		# Get the post collection
		posts = get_db().moogloof.posts

		# Get post with matching title
		try:
			post = posts.find_one({
				"_id": ObjectId(_id)
			})
		except InvalidId:
			abort(404)

		if not post:
			# No post with title exists
			abort(404)
		else:
			saved = {
				"_id": _id,
				"title": post["title"],
				"content": post["content"]
			}

			# Get thumbnail if saved
			if "thumbnail" in post:
				saved["thumbnail"] = post["thumbnail"]

			# Get post edit form
			if request.method == "POST":
				# Clean the form
				post_title = request.form["title"].strip()
				post_content = request.form["content"]
				post_thumbnail = request.form["thumbnail"].strip()

				# Make content saved to form
				saved["content"] = post_content

				# Validate post title
				if post_title == "":
					# Alert user that title cannot be whitespace
					flash("Your title can't just be whitespace bro.")
				elif bool(posts.find_one({"title": post_title})) and post_title != post["title"]:
					# Alert user that post with the same title already exists
					flash("Post with the same title exists.")
				else:
					# Edit post
					edit_post = {
						"title": post_title,
						"content": post_content
					}

					# Unset
					edit_post_unset = {}

					# Edit thumbnail if one is added
					if post_thumbnail:
						edit_post["thumbnail"] = post_thumbnail
					else:
						edit_post_unset["thumbnail"] = ""

					# Insert post into collection
					posts.update_one({"_id": post["_id"]}, {"$set": edit_post, "$unset": edit_post_unset})

					# Redirect to the page of the post
					return redirect(url_for("blog", _id=post["_id"]))
			# Render post edit
			return render_template("post_edit.html", header="edit post", saved=saved)
	else:
		# Return with error if not logged in
		abort(403)

@app.route("/blog/<_id>/delete", methods=["GET"])
def delete_blog(_id):
	# Check if user is logged in
	if "logged-id" in session and session["logged-id"] == LOGGED_ID:
		# Get the post collection
		posts = get_db().moogloof.posts

		# Get post with matching id
		try:
			post = posts.find_one({
				"_id": ObjectId(_id)
			})
		except InvalidId:
			abort(404)

		if not post:
			# No post with id exists
			abort(404)
		else:
			# Delete post
			posts.delete_one({"_id": ObjectId(_id)})

			# Redirect to the blog list
			return redirect(url_for("blog"))
	else:
		# Return with error if not logged in
		abort(403)

# Comment on blog
@app.route("/blog/<_id>/comment", methods=["POST"])
def comment_blog(_id):
	# Get the database
	db = get_db()

	# Get post with matching id
	try:
		post = db.moogloof.posts.find_one({
			"_id": ObjectId(_id)
		})
	except InvalidId:
		abort(404)

	if not post:
		# No post with id exists
		abort(404)
	else:
		# Clean form data
		comment_name = request.form["name"].strip()
		comment_email = request.form["email"]
		comment_website = request.form["website"]
		comment_content = request.form["content"]

		# Make new comment
		new_comment = {
			"post": ObjectId(_id),
			"date": datetime.now(timezone.utc),
			"name": comment_name,
			"email": comment_email,
			"website": comment_website,
			"content": comment_content,
			"approved": False
		}

		# Insert new comment
		inserted_comment = db.moogloof.comments.insert_one(new_comment)

		# Redirect to post with pending message
		flash("Thank you for your comment! Your comment will be visible once it is reviewed and approved by an admin.")
		return redirect(url_for("blog", _id=post["_id"]))

# Project page
@app.route("/projects")
@app.route("/projects/<_id>")
def projects(_id=None):
	# Get the project and the project
	projects_q = get_db().moogloof.projects

	if not _id:
		projects_q = projects_q.find()

		# Render projects
		return render_template("projects.html", header="projects", projects=projects_q)
	else:
		# Get the thingy
		try:
			project = projects_q.find_one({
				"_id": ObjectId(_id)
			})
		except InvalidId:
			abort(404)

		# Render the project
		return render_template("project_page.html", header="project page for {}".format(project["title"]), project=project)

# Create project page
@app.route("/projects/create", methods=["GET", "POST"])
def create_project():
	# Check if user is logged in
	if "logged-id" in session and session["logged-id"] == LOGGED_ID:
		# Saved is the form data to keep in case of invalid inputs
		saved = {}

		# Check if the form was submitted
		if request.method == "POST":
			# Clean the form
			project_title = request.form["title"].strip()
			project_description = request.form["description"]
			# Get the database
			db = get_db()

			# Make content saved to form
			saved["description"] = project_description

			# Validate post title
			if project_title == "":
				# Alert user that title cannot be whitespace
				flash("Your title can't just be whitespace bro.")
			elif bool(db.moogloof.projects.find_one({"title": project_title})):
				# Alert user that project with the same title already exists
				flash("Project with the same title exists.")
			else:
				# Create a new project
				new_project = {
					"title": project_title,
					"description": project_description
				}

				# Insert project into collection
				inserted_project = db.moogloof.projects.insert_one(new_project)

				# Redirect to the page of the post
				return redirect(url_for("projects", _id=inserted_project.inserted_id))

		# Render the create page template
		return render_template("project_create.html", saved=saved)
	else:
		# Return with error if not logged in
		abort(403)

# Edit blog page
@app.route("/projects/<_id>/update", methods=["GET", "POST"])
def edit_project(_id):
	# Check if user is logged in
	if "logged-id" in session and session["logged-id"] == LOGGED_ID:
		# Get the post collection
		projects = get_db().moogloof.projects

		# Get post with matching title
		try:
			project = projects.find_one({
				"_id": ObjectId(_id)
			})
		except InvalidId:
			abort(404)

		if not project:
			# No post with title exists
			abort(404)
		else:
			saved = {
				"_id": _id,
				"title": project["title"],
				"description": project["description"]
			}

			# Get post edit form
			if request.method == "POST":
				# Clean the form
				project_title = request.form["title"].strip()
				project_description = request.form["description"]

				# Make content saved to form
				saved["description"] = project_description

				# Validate project title
				if project_title == "":
					# Alert user that title cannot be whitespace
					flash("Your title can't just be whitespace bro.")
				elif bool(projects.find_one({"title": project_title})) and project_title != project["title"]:
					# Alert user that projects with the same title already exists
					flash("Project with the same title exists.")
				else:
					# Edit post
					edit_project = {
						"title": project_title,
						"description": project_description
					}

					# Insert post into collection
					projects.update_one({"_id": project["_id"]}, {"$set": edit_project})

					# Redirect to the page of the post
					return redirect(url_for("projects", _id=project["_id"]))
			# Render post edit
			return render_template("project_edit.html", header="edit project", saved=saved)
	else:
		# Return with error if not logged in
		abort(403)

# Comment review page
@app.route("/comments", methods=["GET", "POST"])
def comments():
	# Check if user is logged in
	if "logged-id" in session and session["logged-id"] == LOGGED_ID:
		comments_q = get_db().moogloof.comments
		# Check if changing comment status
		if request.method == "POST":
			comment = comments_q.find_one({
				"_id": ObjectId(request.form["id"])
			})

			comments_q.update_one({"_id": comment["_id"]}, {"$set": {"approved": request.form["visible"] == "true"}})

			return app.response_class(response=json_util.dumps({}), status=200, mimetype='application/json')

		# Get comments
		comments_q = comments_q.find().sort("date", -1)

		# Render the comments page template for admins
		return render_template("comments.html", header="comments", comments=comments_q)
	else:
		abort(403)

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

# CS429 Page for the stuff
@app.route("/gheith/<course_id>")
def cs429(course_id):
	progs = []
	i = 1

	while True:
		prog_url = f"https://www.cs.utexas.edu/~gheith/{course_id}_p{i}.html"
		check_prog = requests.get(prog_url)

		if check_prog.status_code == 200:
			progs.append(i)
		else:
			break

		i += 1

	return render_template("cs429.html", header="CS429 Stats", progs=progs, course_id=course_id)

@app.route("/gheith/prog/<course_id>/<_id>")
def cs429_prog(course_id, _id):
	prog_url = f"https://www.cs.utexas.edu/~gheith/{course_id}_p{_id}.html"
	prog_content = BeautifulSoup(requests.get(prog_url).text, "html.parser")

	prog_table = prog_content.find("table", class_="results")
	prog_data = prog_content.find_all("tr")

	prog_data = filter(lambda x: x.get("data-alias") is not None, prog_data)

	submits = []
	tests = {}

	for student in prog_data:
		passes = 0
		chosen_passes = 0
		fails = 0
		chosen_fails = 0
		total_pass_time = 0
		total_fail_time = 0

		student_data = student.find_all("td")

		for datum in student_data:
			datum_type = datum.get("class")

			if datum_type is not None and "alias" not in datum_type and "row-pin" not in datum_type:
				time_passed = float(datum.get("title").split()[-1][:-1])

				if "pass" in datum_type:
					total_pass_time += time_passed
					passes += 1
					if "chosen" in datum_type:
						chosen_passes += 1
				else:
					total_fail_time += time_passed
					fails += 1
					if "chosen" in datum_type:
						chosen_fails += 1

		total_submits = passes + fails

		stu_id = student.get("data-alias")
		submits.append({
			"id": stu_id,
			"avg_runtime": ((total_pass_time + total_fail_time) / total_submits) if total_submits != 0 else "NaN",
			"avg_success_runtime": (total_pass_time / passes) if passes != 0 else "NaN",
			"avg_fail_runtime": (total_fail_time / fails) if fails != 0 else "NaN",
			"success_rate": (passes / total_submits) if total_submits != 0 else "NaN",
			"chosen_success_rate": (chosen_passes / (chosen_fails + chosen_passes)) if chosen_fails + chosen_passes != 0 else "NaN"
		})

	# Check for previous and next progs
	prog_id = int(_id)
	prev_prog = None
	next_prog = None

	# Check previous prog
	if prog_id > 1:
		prev_url = f"https://www.cs.utexas.edu/~gheith/{course_id}_p{prog_id-1}.html"
		prev_check = requests.get(prev_url)
		if prev_check.status_code == 200:
			prev_prog = {
				'url': url_for('cs429_prog', course_id=course_id, _id=prog_id-1),
				'name': f'Prog {prog_id-1}'
			}

	# Check next prog
	next_url = f"https://www.cs.utexas.edu/~gheith/{course_id}_p{prog_id+1}.html"
	next_check = requests.get(next_url)
	if next_check.status_code == 200:
		next_prog = {
			'url': url_for('cs429_prog', course_id=course_id, _id=prog_id+1),
			'name': f'Prog {prog_id+1}'
		}

	return render_template(
		"prog.html",
		header=f"{ course_id } Prog {_id}",
		submits=submits,
		tests=tests,
		course_url=url_for('cs429', course_id=course_id),
		course_name=course_id,
		prev_prog=prev_prog,
		next_prog=next_prog
	)

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

