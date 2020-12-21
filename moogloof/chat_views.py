# Package imports
from bson.objectid import ObjectId
from datetime import datetime, timezone
from flask import render_template, abort, request, url_for, redirect

# App imports
from moogloof.app import app
from moogloof.db import get_db


# Chat dashboard page
@app.route("/", subdomain="chat")
@app.route("/c/<hid>", subdomain="chat")
def chats(hid=None):
	# Get the message collection
	messages = get_db().moogloof.messages

	if not hid:
		message_q = messages.find().sort("date", -1)

		# Different handling depending on message id
		return render_template("chat/chats.html", messages=message_q)
	else:
		# Get chat with matchiing head id
		message = messages.find_one({
			"_id": int(hid)
		})

		if not message:
			# No message with id
			abort(404)
		else:
			# Render message
			return render_template("chat/message.html", header="message", message=message)

# Chat create form
@app.route("/create", subdomain="chat", methods=["GET", "POST"])
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
			"_id": new_id
		}

		# Set author of message if given
		if message_author != "":
			new_message["author"] = message_author

		# Validate message content
		if message_content == "":
			# Alert user that content cannot be empty or just whitespace
			flash("Actually put something in there.")
		else:
			# Insert message into collection
			db.moogloof.messages.insert_one(new_message)

			# Redirect to the message page
			return redirect(url_for("chats", hid=new_id))

		# Redirect to chat page if invalid
		return redirect(url_for("chats"))
	else:
		abort(403)

