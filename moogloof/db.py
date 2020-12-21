# Package imports
from pymongo import MongoClient
from flask import g

# App imports
from moogloof.app import app
from moogloof.config import MONGO_URI


# Fetch db
def get_db():
	# Open a database if not already present
	if 'db' not in g:
		g.db = MongoClient(MONGO_URI)

	# Return database
	return g.db

# Close db
@app.teardown_appcontext
def teardown_db(e):
	# After exitting app context, get rid of database
	db = g.pop('db', None)

	# Close the database connection
	if db is not None:
		db.close()

