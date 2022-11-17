# Package imports
from bson.objectid import ObjectId
from datetime import datetime, timezone
from flask import render_template, abort, request, url_for, redirect
import pymongo

# App imports
from moogloof.app import app
from moogloof.db import get_db


# Chat dashboard page
@app.route("/chat")
@app.route("/chat/c/<hid>")
def chats(hid=None):
	# Get the message collection
	messages = get_db().moogloof.messages

	if not hid:
		message_q = messages.find({"head": {"$exists": False, "$ne": True}}).sort("date", -1)

		# Different handling depending on message id
		return render_template("chat/chats.html", messages=message_q)
	else:
		# Get chat with matchiing head id
		message = messages.find_one({
			"_id": int(hid)
		})

		# Get replies
		replies = messages.find({
			"head": hid
		}).sort("date", pymongo.DESCENDING)

		if not message:
			# No message with id
			abort(404)
		else:
			# Render message
			return render_template("chat/message.html", header="message", message=message, replies=replies)

# Chat create form
@app.route("/chat/create", methods=["GET", "POST"])
def create_chat():
	if request.method == "POST":
		# Clean the form
		message_content = request.form["content"].strip()
		message_author = request.form["name"].strip()

		# Get the database
		db = get_db()

		# Generate new id
		new_id = db.moogloof.messages.find().sort("date", -1).limit(1)

		if new_id.count() > 0:
			new_id = list(new_id)[0]["_id"] + 1
		else:
			new_id = 0

		# Create new message
		new_message = {
			"date": datetime.now(timezone.utc),
			"content": message_content,
			"_id": new_id,
		}

		# Set author of message if given
		if message_author != "":
			new_message["author"] = message_author

		# Check if message is reply or not
		if "head" in request.form.keys():
			new_message["head"] = request.form["head"]

		# Validate message content
		if message_content == "":
			# Alert user that content cannot be empty or just whitespace
			flash("Actually put something in there.")
		else:
			# Insert message into collection
			db.moogloof.messages.insert_one(new_message)

			# Redirect to the message page
			return redirect(request.referrer)

		# Redirect to chat page if invalid
		return redirect(url_for("chats"))
	else:
		abort(403)

